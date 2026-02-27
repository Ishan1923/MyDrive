import boto3
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserFile
from .forms import FileUploadForm

def get_s3_file_versions(file_key):
    """Fetches all versions of a specific file from the S3 bucket."""
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        aws_session_token=settings.AWS_SESSION_TOKEN,
        region_name=settings.AWS_S3_REGION_NAME,
        verify=getattr(settings, 'AWS_S3_VERIFY', True) # Uses your setting
    )
    try:
        response = s3.list_object_versions(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, 
            Prefix=file_key
        )
        # Returns a list of version dictionaries
        return response.get('Versions', [])
    except Exception as e:
        print(f"Error fetching versions: {e}")
        return []

@login_required
def manage_files(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save(commit=False)
            new_file.owner = request.user
            new_file.save()
            return redirect('manage_files')
    else:
        form = FileUploadForm()

    # Get user's files
    user_files = UserFile.objects.filter(owner=request.user)
    
    # Bundle each file with its version history
    files_with_versions = []
    for f in user_files:
        versions = get_s3_file_versions(f.file.name)
        files_with_versions.append({
            'obj': f,
            'versions': versions
        })

    return render(request, 'file_manager.html', {
        'form': form, 
        'files_with_versions': files_with_versions
    })
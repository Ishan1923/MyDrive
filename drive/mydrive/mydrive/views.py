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
    
    # Ordered by newest first so the dictionary keeps the latest database entry
    all_files = UserFile.objects.filter(owner=request.user).order_by('-id')
    
    unique_files = {}
    for f in all_files:
        if f.file.name not in unique_files:
            # 1. Fetch the version history from S3
            versions = get_s3_file_versions(f.file.name)
            
            # 2. Attach the history to the file object directly
            f.s3_versions = versions 
            
            # 3. Store in dictionary
            unique_files[f.file.name] = f
            
    return render(request, 'file_manager.html', {
        'form': form, 
        'files': unique_files.values()
    })
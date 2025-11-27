import os
import tempfile
import zipfile
import shutil
from io import StringIO, BytesIO

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import BackupOptionsForm, RestoreUploadForm


@staff_member_required
def backup_restore_home(request):
    """Show page with Backup and Restore forms."""
    backup_form = BackupOptionsForm()
    restore_form = RestoreUploadForm()

    if request.method == 'POST':
        if 'do_backup' in request.POST:
            return backup_view(request)
        elif 'do_restore' in request.POST:
            return restore_view(request)

    return render(
        request,
        'backup/backup_restore.html',
        {'backup_form': backup_form, 'restore_form': restore_form}
    )


def _generate_dumpjson(temp_dir):
    """Dump full database to JSON file."""
    fixture_path = os.path.join(temp_dir, 'site_backup.json')
    out_stream = StringIO()
    call_command('dumpdata', stdout=out_stream, indent=2, natural_foreign=True, natural_primary=True)
    with open(fixture_path, 'w', encoding='utf-8') as f:
        f.write(out_stream.getvalue())
    return fixture_path


def _add_media_to_zip(zipf):
    """Add all media files under MEDIA_ROOT to zip under 'media/'."""
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if not media_root or not os.path.exists(media_root):
        return
    for root, dirs, files in os.walk(media_root):
        for file in files:
            fullpath = os.path.join(root, file)
            arcname = os.path.relpath(fullpath, settings.MEDIA_ROOT)
            zipf.write(fullpath, os.path.join('media', arcname))


@staff_member_required
def backup_view(request):
    """Create backup ZIP and return as download."""
    if request.method != 'POST':
        return HttpResponseBadRequest("Backup must be requested via POST.")

    form = BackupOptionsForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Invalid backup options.")
        return redirect(reverse('backup:backup_home'))

    temp_dir = tempfile.mkdtemp(prefix='site_backup_')
    try:
        json_path = _generate_dumpjson(temp_dir)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(json_path, arcname='data/site_backup.json')
            _add_media_to_zip(zipf)
            zipf.writestr('README.txt', "SafiyaScripts Backup\nContains data and media files")

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="safiyascripts_backup.zip"'
        return response
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def _extract_media_from_zip(temp_dir, zipf):
    """Extract media files from ZIP to temp_dir."""
    extracted_media_dir = os.path.join(temp_dir, 'extracted_media')
    os.makedirs(extracted_media_dir, exist_ok=True)

    for member in zipf.namelist():
        if member.startswith('media/'):
            relpath = member[len('media/'):]
            if not relpath:
                continue
            target_path = os.path.join(extracted_media_dir, relpath)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with zipf.open(member) as source, open(target_path, 'wb') as target:
                shutil.copyfileobj(source, target)
    return extracted_media_dir


@staff_member_required
def restore_view(request):
    """Handle uploaded backup ZIP and restore.Thanks"""
    if request.method != 'POST':
        return HttpResponseBadRequest("Restore must be submitted via POST.")

    form = RestoreUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Please upload a valid backup ZIP.")
        return redirect(reverse('backup:backup_home'))

    zip_file = form.cleaned_data['zip_file']

    try:
        zipf = zipfile.ZipFile(zip_file)
    except zipfile.BadZipFile:
        messages.error(request, "Uploaded file is not a valid ZIP.")
        return redirect(reverse('backup:backup_home'))

    temp_dir = tempfile.mkdtemp(prefix='site_restore_')
    try:
        json_member = None
        for name in zipf.namelist():
            if name.endswith('site_backup.json'):
                json_member = name
                break
        if not json_member:
            messages.error(request, "ZIP does not contain site_backup.json.")
            return redirect(reverse('backup:backup_home'))

        zipf.extract(json_member, path=temp_dir)
        extracted_json_path = os.path.join(temp_dir, json_member)

        # Restore database
        try:
            call_command('loaddata', extracted_json_path)
        except Exception as e:
            messages.error(request, f"Error loading data fixture: {e}")
            return redirect(reverse('backup:backup_home'))

        # Restore media
        extracted_media_dir = _extract_media_from_zip(temp_dir, zipf)
        if os.path.exists(extracted_media_dir):
            media_root = getattr(settings, 'MEDIA_ROOT', None)
            if media_root:
                for root, dirs, files in os.walk(extracted_media_dir):
                    for file in files:
                        src = os.path.join(root, file)
                        rel = os.path.relpath(src, extracted_media_dir)
                        dst = os.path.join(media_root, rel)
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst)

        messages.success(request, "Restore completed successfully.")
        return redirect(reverse('backup:backup_home'))
    finally:
        zipf.close()
        shutil.rmtree(temp_dir, ignore_errors=True)

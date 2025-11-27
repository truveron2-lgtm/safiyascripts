from django import forms

class BackupOptionsForm(forms.Form):
    """
    Full system backup (database + media)
    """
    # We can keep this if you want optional app backup in the future
    apps = forms.CharField(
        required=False,
        label="App labels (optional)",
        help_text="Optional: enter app labels to backup only specific apps (comma separated). Leave blank for full backup."
    )


class RestoreUploadForm(forms.Form):
    zip_file = forms.FileField(
        label="Backup ZIP file",
        help_text="Upload the ZIP produced by the backup tool."
    )

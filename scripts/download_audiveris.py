import os
import subprocess
import urllib.request

msi_url = 'https://github.com/Audiveris/audiveris/releases/download/5.11.0/Audiveris-5.11.0-windowsConsole-x86_64.msi'
local_msi = 'tools/AudiverisConsole.msi'
target_dir = os.path.abspath('tools/audiveris')

print('Downloading Audiveris Console MSI...')
urllib.request.urlretrieve(msi_url, local_msi)

print('Extracting MSI via msiexec /a...')
os.makedirs(target_dir, exist_ok=True)
cmd = f'msiexec /a "{os.path.abspath(local_msi)}" /qb TARGETDIR="{target_dir}"'
print('Running:', cmd)
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print('msiexec return code:', res.returncode)
print('msiexec stdout:', res.stdout)
print('msiexec stderr:', res.stderr)

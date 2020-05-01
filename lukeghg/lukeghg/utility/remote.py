from paramiko import SSHClient
import pandas as pd

class RemoteFile:
    def __init__(self):
        self.ssh=None
    def __del__(self):
        if self.ssh:
            self.ssh.close()
    def open_remote_file(self,server:str,file_path:str):
        """"
        Open connection to remote server, open the remote file.
        Return the file descriptor and the ssh connection.
        Note: Don't close connections, read_remote_file will use them 
        """
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.connect(server)
        sftp = self.ssh.open_sftp()
        f = sftp.open(file_path,'r')
        return (f)
    def read_remote_file(self,server:str,file_path:str):
        """
        Get the file descriptor from remote server and
        read the file to pandas dataframe. Close the file
        and the remote connection (a.k.a socket)
        Return the dataframe 
        """
        f = self.open_remote_file(server,file_path)
        df = pd.read_csv(f,delim_whitespace=True)
        f.close()
        return df


from paramiko import SSHClient
import pandas as pd

class RemoteFile:
    def __init__(self):
        self.ssh=None
    def __del__(self):
        if self.ssh:
            self.ssh.close()
    def open_remote_file(self,server:str,file_path:str):
        """
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
    def read_remote_file_df(self,server:str,file_path:str):
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
    def df_to_list(self,df,acc:int=-1):
        """
        df: turn the dataframe read by 'read_remote_file' to list of 
        list of dataframe rows. The 'acc' rounds decimals used
        (e.g. GHG uses 6 decimals for CRFReporter). 
        acc: by default no rounding (acc=-1), 
        otherwise rounding to accuracy denoted by acc.
        Note when rounding it assumed df contains only numbers (no GHG notation keys for example).
        Return the list of rows: [row_1,...,row_n] where each row is a list of row values 
        """
        lss =[]
        for index in range(len(df.index)):
            lss.append(list(df.loc[index,]))
        #For example '.6f'
        if acc >= 0:
            acc_str='.'+str(acc)+'f'
            lss = [list(map(lambda x: format(float(x),acc_str),ls)) for ls in lss]
        return lss
    def list_to_str(self,ls):
        """Change list element datatype to string"""
        ls = [str(x) for x in ls]
        return ls
    def read_remote_file(self,server:str,file_path:str,acc:int=-1):
        """
        Read remote (GHG csv) file to list of list of data rows
        server: remote server
        file_path: full path to data file
        acc: accuracy in decimals after rounding, default -1 means no rounding
        """
        df = self.read_remote_file_df(server,file_path)
        lss = self.df_to_list(df,acc)
        return lss
    def read_remote_file_as_str(self,server:str,file_path:str,acc:int=-1):
        """
        Read remote (GHG csv) file to list of list of data rows as strings
        server: remote server
        file_path: full path to data file
        acc: accuracy in decimals after rounding, default -1 means no rounding
        """
        df = self.read_remote_file_df(server,file_path)
        lss = self.df_to_list(df,acc)
        lss = [self.list_to_str(ls) for ls in lss]
        return lss

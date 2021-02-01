import xroms
import dask_mpi
from dask.distributed import Client
#from dask_jobqueue import LSFCluster
from distributed import Client



class dataset():

    def __init__(self, envDict, logger=None):
        self._name = 'Base'
        self._title = 'Base'
        self.ds = None
        self.client = None
        self.logger = logger

    def start_daskclient(self, cluster_type='MPI'):
        self.client = self._get_dask_client(cluster_type)

    def stop_daskclient(self):
        self.client.close()

    def open_dataset(self, files):
        self.ds = self._get_dataset(files)

    def _get_dask_client(self, cluster_type):
        client = None

        if cluster_type == 'MPI':
            dask_mpi.initialize()
            client = Client()
        elif cluster_type == 'LSF':
            # TODO: see if this is required
            #cluster = LSFCluster(cores=21, processes=7, memory='106GB', interface='ib0', use_stdin=True,
            #                     walltime="02:00", job_extra=['-U agopal'])
            #client = Client(cluster)
            client = Client()
        else:
            client = Client(n_workers=8, threads_per_worker=1, memory_limit='6GB')

        return client

    def _get_dataset(self, files):
        """

        :rtype: object
        :param test: 
        :return:
        """

        self.logger.debug('calling checkHistoryFiles for model case')


        ds = None
        ds = xroms.open_mfnetcdf(files, chunks={'ocean_time': 30})

        return ds

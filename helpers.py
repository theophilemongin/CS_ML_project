import h5py
import numpy as np
import pandas as pd

# HELPERS

def print_bis(txt):
    print(txt, end='\x1b[1K\r')
    
def print_ter(txt):
    print(f"\n{txt}")

    
def make_timeline(freq):
    """
    ARGS:
        freq (int): frequency in Hertz
    
    RETURNS:
        (pd.timedelta_range) : timestamps for a signal sampled at <freq> Hz for 30 seconds
    """
    return pd.timedelta_range(start='0s', end='30s', periods=freq*30)


def make_full_timeline(windows, freq):
    # test there is no missing data
    deltas = np.unique(np.diff(windows))
    assert (len(deltas) == 1) and (int(deltas[0]) == 1)
    return pd.timedelta_range(start='0s',
                              end=pd.to_timedelta('30s') * (windows[-1] + 1),
                              periods=freq * 30 * (windows[-1] + 1))

def get_subject_ids(h5_file):
    return np.unique(h5_file["index"][:])

    
def get_subject_boundaries(h5_file, subject_id, ready_to_use=True):
    """
    Helper function to select data relating to a given subject (on numpy arrays)
    
    ARGS:
        h5_file (h5py.File)
        subject_id (int)
        ready_to_use (bool, default=True): return a slice or a tuple
        
    RETURNS:
        subject_boundaries : (slice) (index_start, index_end+1) if <ready_to_use>
                             (tuple) (index_start, index_end) if not <ready_to_use>
                        
    """
    sids = h5_file['index'][:]
    start = np.argmax(sids == subject_id)
    end = len(sids) - 1 - np.argmax(sids[::-1] == subject_id)
    
    indexers = h5_file['index_absolute'][:]
    start = indexers[start]
    end = indexers[end]
    if ready_to_use:
        return slice(start, end + 1) # for numpy arrays
    return (start, end)


def get_subject_feature_signals(h5_file, subject_id, feature, as_timeseries=False):
    """
    Get the full timeseries for a given (subject_id, feature) pair.
    
    ARGS:
        h5_file (h5py.File)
        subject_id (int)
        feature (str)
        
    RETURNS:
        timeseries : (pd.Series if <as_timeseries>) represents the <feature> timeseries of the subject 
                     (list[np.array[?]] if not <as_timeseries>) list of <feature> signals from the subject
    """
    # Fetch subject boundaries
    boundaries = get_subject_boundaries(h5_file, subject_id)
    # Retrieve samples
    feature_timeseries = h5_file[feature][boundaries]
    if not as_timeseries:
        return feature_timeseries
    feature_timeseries = np.concatenate(feature_timeseries, axis=0)
    # Build timeline
    feature_frequency = FREQUENCIES[feature]
    windows = h5_file['index_window'][boundaries]
    timeline = make_full_timeline(windows, feature_frequency)
    return pd.Series(data=feature_timeseries, index=timeline)


def get_subject_sleep_stage(subject_id, h5_train):
    start, end = get_subject_boundaries(h5_train, subject_id, ready_to_use=False)
    return y_train.loc[start:end] # because loc includes <end> (different behaviour than numpy arrays)
    


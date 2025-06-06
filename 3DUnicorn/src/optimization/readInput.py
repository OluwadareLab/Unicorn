import numpy as np
import os

def read_input(INPUT_FILE, output_path):
    """
    Load and process the contact matrix from a file.
    
    Args:
    - INPUT_FILE (str): Path to the input file.
    - output_path (str): Path to the output directory.
    
    Returns:
    - lstCons (ndarray): Processed contact list.
    - n (int): Number of unique positions.
    - mapping (ndarray): Mapping of positions to absolute ids.
    """
    
    # Read the file
    filename = INPUT_FILE
    cont = np.loadtxt(filename)
    
    # Assume input is in tuple format
    if cont.shape[1] == 3:
        print('Input is in Tuple format')
    else:
        raise ValueError("Input must be in tuple format with 3 columns: position1, position2, contact_frequency")

    pos = []
    
    # Remove zero contacts and NaN, and exclude self-interactions
    ind_greater_IF = np.where((cont[:, 2] > 0) & (~np.isnan(cont[:, 2])) & (cont[:, 0] != cont[:, 1]))
    contact = cont[ind_greater_IF]
    pos = np.hstack((contact[:, 0], contact[:, 1]))

    # lstCons is the list of filtered contacts
    lstCons = contact
    
    # Sort and get unique positions
    pos = np.unique(pos)
    
    # Number of unique positions
    n = len(pos)
    
    # Map positions to absolute ids
    mapping = np.zeros((n, 2))
    for i in range(n):
        mapping[i, 0] = pos[i]
        mapping[i, 1] = i + 1  # 1-based index, consistent with MATLAB
    
    # Create a mapping dictionary for position to id
    Map = dict(zip(mapping[:, 0], mapping[:, 1]))
    
    # Replace positions with their mapped IDs
    for i in range(len(lstCons)):
        lstCons[i, 0] = Map[lstCons[i, 0]]
        lstCons[i, 1] = Map[lstCons[i, 1]]

    return lstCons, n, mapping

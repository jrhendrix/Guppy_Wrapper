# Guppy_Wrapper
A hack method for parallelizing Guppy on a CPU-based cluster

## Introduction
Guppy is a Basecaller designed by Oxford Nanopore Technologies (ONT) to translate the raw signal measurements from an ONT device such as a MinION into bases. Though applauded for its high accuracy, Guppy is notoriously slow when run on a CPU-based system. Guppy is optimized for a GPU-based system, specifically the GPUs created by NVIDIA. However, these NVIDIA GPUs can be expensive especially for researchers who already have access to a CPU-based High Performance Computing (HPC) cluster. 

This script is meant to fill a niche for those who want to quickly run Guppy on a CPU-based HPC cluster. 

## Requirements
* Guppy software
* Python
* Access to HPC cluster
* Linux


## Usage
As input, the script requires a path to the direcotry of FAST5 files and the path to the Guppy basecaller
Basic Usage:
`python wrap_Guppy_CPU.py -g path/to/guppy_basecaller -i FAST5_directory`
To specify a different flowcell or kit:
`python wrap_Guppy_CPU.py -g path/to/guppy_basecaller -i FAST5_directory -f FLO-MIN106 -k SQK-LSK109`

After running the command, the FASTQ files will be in their own subdirecotries. Run the following command to gather all of the basecalled reads into one file.
`cat `

## Cautionary Note
This script will call Guppy for each file in the FAST5 directory. In other words, if there are 100 files, then this script will initiate 100 jobs onto the cluster. If you are sharing the HPC with other users, consider splitting the FAST5 directory into smaller batches to avoid clogging the que. 


## Implementation
* Create sub directory for each .fast5 file
*     Guppy takes as input a directory of .fast5 files, meaning that it cannot be given the path to an individual file. To call Guppy on individual files, the script first creates a sub-directory for each .fast5 file.
* Create a file link
*     The sub directory should contain the .fast5 file, but copying all this data would be a waste of time and space on the drive. Therfore, the sub directories contain a link to its respective .fast5 file. This method also avoids errors that could occur if trying to move all of the data. 
* Call Guppy
*   The script then calls guppy, passing the subdirectory as the input and save space
*   It is up to the user to specify the flowcell and kit so that Guppy will use the correct model.






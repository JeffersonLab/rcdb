from os import walk
from os import path
import os
import click
import glob
from rcdb.app_context import minmax_run_range, parse_run_range
from rcdb.provider import  RCDBProvider
from rcdb.rcdb_cli.context import pass_rcdb_context
import json

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def read_run_directories(mask, run_min, run_max):
    run_dirs = glob.glob(mask)

    # Dict in form {run_number:[evio files]}
    run_files = {}
    
    # Find all evio files in a given run range
    click.echo(f"{'Run':<20}  Number of evio files")
    for run_dir in run_dirs:

        # Extract run number
        run_dir_name = path.basename(run_dir)
        try:
            run_num = int(run_dir_name[3:])
        except Exception as ex:
            click.echo(f"Error extracting run from directory '{run_dir_name}'")
            continue

        # Skip this run if needed
        if run_num < run_min or run_num > run_max:
            continue

        # Fill resulting array
        data_files = glob.glob(f'{run_dir}/*.evio')
        run_files[run_num] = data_files
        
        # Pretty print
        click.echo(f"{path.basename(run_dir):<20} {len(data_files)}")

    return run_files

@click.command()
@click.option('--run-range', required=False, default=None)
@click.option('--mask', required=False, default="/gluex/data/rawdata/all/Run*111*")
@click.option('--save-list', required=False, default=None, help="Save found evio files to json file with this name")
@click.option('--load-list', required=False, default=None, help="Instead of scanning, load eviofiles from a list")
@click.option('--execute', is_flag=True, required=False, default=False, help="Instead of scanning, load eviofiles from a list")
@pass_rcdb_context
def evio_files(ctx, run_range, mask, save_list, load_list, execute):
    """ 
    Example of usage: 
      # search /mss and save evio files to a json file list
      rcdb repair evio-files --run-range=0 --mask="/mss/halld/RunPeriod-2022-08/rawdata/Run*" --save-list RunPeriod-2022-08_evio_files.json

      # same but for all run ranges
      rcdb repair evio-files --run-range=0 --mask="/mss/halld/RunPeriod*/rawdata/Run*" --save-list all_evio_files.json

      # load files and show what is to be done (no fix though)
      rcdb -c mysql://rcdb@hallddb/rcdb repair evio-files --load-list 2023_01_18_all_evio_files.json

      # add --execute to make changes in DB
      # (hallddb is readonly and this command will fail, use the correct db and password)
      rcdb -c mysql://rcdb@hallddb/rcdb repair evio-files --load-list 2023_01_18_all_evio_files.json --execute
    
    """
    click.echo("Executing evio-files with:")
    click.echo((run_range, mask, save_list, load_list, execute))

    run_min, run_max = minmax_run_range(parse_run_range(run_range))
    click.echo(f"Scanning all runs between: {run_min} - {run_max}")

    # Get files from list or from directories
    if load_list:
        with open(load_list) as list_file:
            click.echo(f"Loading json from '{load_list}'")
            run_files = json.load(list_file)
    else:
        run_files = read_run_directories(mask, run_min, run_max)

    # Should we just save files? 
    if save_list:
        with open(save_list, 'w') as save_file:
            json.dump(run_files, save_file)
            return
    
    # Now iterate over runs
    db = ctx.db
    assert db is not None
    assert isinstance(db, RCDBProvider)
    click.echo(f"\n\n PROCESSING {len(run_files)} RUNS")
    for run_num, evio_files in run_files.items():
        # Skip this run if needed
        if int(run_num) < run_min or int(run_num) > run_max:
            continue

        run = db.get_run(run_num)

        if run is None: 
            print(f"WARNING! Run {run_num} exists on disk, but not in DB")
            click.echo(f"run has: {len(evio_files)} evio files. Checking...")
            # for file_path in evio_files:
            #                 # extract file size: 
            #     file_size = os.stat(file_path)
            #     print(f"Size of file {file_path} : {sizeof_fmt(file_size.st_size)}")
            continue

        click.echo(f"RUN # {run.number}")


        evio_files.sort()
        # for file_path in evio_files:
        #                 # extract file size: 
        #     file_size = os.stat(file_path)            
        #     print(file_path)
            
        evio_files_count_cnd = run.get_condition("evio_files_count")
        if not evio_files_count_cnd:
            print("  No condition 'evio_files_count' found for run")
            print(f"  Adding evio_files_count = {len(evio_files)}")
            if execute:
                db.add_condition(run, "evio_files_count", len(evio_files))
        else:
            if evio_files_count_cnd.value != len(evio_files):
                "  Number of files mistmatch:"
                print(f"  {evio_files_count_cnd.value} = {len(evio_files)}")
        
        evio_last_file_cnd = run.get_condition("evio_last_file")
        if not evio_last_file_cnd and evio_files:
            print("  No condition 'evio_last_file' found for run")
            print(f"  Adding evio_last_file = {evio_files[-1]}")
            if execute:
                db.add_condition(run, "evio_last_file", evio_files[-1])

        


    
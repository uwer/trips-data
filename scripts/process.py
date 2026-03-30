from pathlib import Path
import os, json, sys

import shutil
import tempfile
import zipfile
from datetime import date

'''
assemble the data packages used by trips and qgis-trips
hence target is either 'qgis' or 'trips'

example 

'core/coredataEPSG4326.fgb.v2.3.oz' 'qgis' 'user/bathy/contour18m2poly,user/nsw/port_nsw,user/oz/oz_ports' '2.3' 

'''
targets = ['qgis','trips']
if __name__ == "__main__":
    
    
    
    if len(sys.argv) < 3:
        print("insufficient arguments ")
        sys.exit(1)
        
    cdw = Path(os.getcwd())
    
    corepackagepath = sys.argv[1]
    target = sys.argv[2]
    if not target in targets:
        raise ValueError(f"unknown target {target} - not in {targets}")
    
    # commaseparated list of path/include
    packageincludes = sys.argv[3].split(',')
    version = sys.argv[4]
    archivetarget = target
    if len(sys.argv) > 5:
        archivetarget = sys.argv[5]
    
    archivename = f'{archivetarget}-data-package.v.{version}-{date.today().strftime("%Y-%m-%d")}'
    
    
    tdir  = Path(tempfile.mkdtemp())
    #tdir = Path(str(tempfile.TemporaryDirectory())
    os.chdir(tdir)
    
    try:
        shutil.copytree(Path(cdw).joinpath(corepackagepath), tdir,dirs_exist_ok=True)
        # add the common files referenced in every configuration 
        shutil.copytree(Path(cdw).joinpath("core/base"), tdir.joinpath("core.fgb.v2"),dirs_exist_ok=True)
        
        
        if target == "qgis":
            includedir = tdir.joinpath('additional')
            includedir.mkdir()
            if len(packageincludes) > 0:
                rootlist = list(tdir.glob("*.json"))
                if len(rootlist) != 1:
                    raise ValueError("Inconsitent package root! Have more than 1 root file")
                
                with rootlist[0].open('r') as fp:
                    rootj = json.load(fp)
                if 'include' in rootj:
                    if not 'additional' in rootj:
                        rootj["include"].append('additional')
                else:
                    rootj["include"]= ['additional']
                    
                with rootlist[0].open('w') as fp:
                    json.dump(rootj,fp,indent=2)
            
        else:
            includedir = tdir.joinpath('user')
            includedir.mkdir()
            
        for pp in packageincludes:
            refpath = cdw.joinpath(pp)
            flist = refpath.parent.glob(f"{refpath.name}*")
            for f in flist:
                if f.is_dir():
                    shutil.copytree(f, includedir.joinpath(f.name))#,dirs_exist_ok=True)
                else:
                    shutil.copy2(f, includedir)
            
        
        os.chdir(cdw)
        shutil.make_archive(archivename, "zip", tdir)
    except:
        print("")
        sys.exit(1)
        
    #finally: # failing - so we just leave for the container to disappear
    #    tdir.unlink()
    
    print(f"{archivename}.zip")
    
    
    
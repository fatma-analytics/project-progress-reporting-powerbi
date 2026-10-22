from pathlib import Path
import pandas as pd
root=Path(__file__).resolve().parents[1]
files=sorted((root/'data/raw').glob('p6_export_*.csv'))
latest=pd.read_csv(files[-1],parse_dates=['BL Start','BL Finish','Start','Finish','Data Date'])
checks={
 'Physical % > 100':int((latest['Physical % Complete']>1).sum()),
 'Completed without Finish':int(((latest['Activity Status']=='Complete')&latest['Finish'].isna()).sum()),
 'BL Finish before BL Start':int((latest['BL Finish']<latest['BL Start']).sum()),
 'Missing Discipline':int(latest['Discipline'].isna().sum()),
 'Duplicate Activity ID':int(latest['Activity ID'].duplicated().sum()),
 'Missing Data Date':int(latest['Data Date'].isna().sum()),
}
print({'snapshot':files[-1].name,'controls':len(checks),'issues':sum(checks.values()),'details':checks})

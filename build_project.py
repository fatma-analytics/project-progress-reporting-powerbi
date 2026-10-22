from pathlib import Path
import pandas as pd, numpy as np, json, shutil, textwrap
from datetime import datetime
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.utils import get_column_letter

ROOT=Path('/home/ubuntu/work/project-progress-reporting-powerbi')
for d in ['data/raw','data/processed','output/figures','excel','powerbi','docs','scripts','sql','data/quality']:
    (ROOT/d).mkdir(parents=True,exist_ok=True)
np.random.seed(42)
start=pd.Timestamp('2025-01-06'); finish=pd.Timestamp('2026-06-30')
data_dates=[pd.Timestamp(x) for x in ['2025-06-30','2025-07-31','2025-08-31','2025-09-30']]
disciplines=['Civil','Mechanical','Piping','Electrical','Instrumentation']; areas=['Area A','Area B','Area C']
rows=[]
for i in range(1,301):
    disc=disciplines[(i-1)%5]; area=areas[((i-1)//5)%3]
    bls=start+pd.Timedelta(days=int(np.random.uniform(0,430)))
    dur=int(np.random.uniform(30,150)); blf=min(bls+pd.Timedelta(days=dur),finish)
    if blf<=bls: blf=bls+pd.Timedelta(days=30)
    budget=round(np.random.uniform(80,1800),1)
    base_rate=np.random.uniform(.82,1.05)
    for dd in data_dates:
        planned=min(1,max(0,(dd-bls).days/max(1,(blf-bls).days)))
        actual=min(1,max(0,planned*base_rate + np.random.normal(0,.025)))
        if dd < bls: actual=0
        if dd >= blf: actual=min(1, max(actual,.96))
        status='Not Started' if actual==0 else ('Complete' if actual>=.995 else 'In Progress')
        start_actual=bls if actual>0 else pd.NaT
        finish_actual=blf if actual>=.995 else pd.NaT
        rows.append({'Activity ID':f'A{i:04d}','Activity Name':f'{disc} work package {i:03d}','WBS Code':f'WBS.{(i-1)//50+1:02d}.{(i-1)//10%5+1:02d}','Discipline':disc,'Area':area,'BL Start':bls,'BL Finish':blf,'Start':start_actual,'Finish':finish_actual,'Planned Duration':dur,'Budgeted Labor Units':budget,'Physical % Complete':round(actual,4),'Activity Status':status,'Data Date':dd})
df=pd.DataFrame(rows)
# Required voluntary anomalies in latest snapshot
latest=data_dates[-1]
ix=df.index[df['Data Date'].eq(latest)]
df.loc[ix[0],'Physical % Complete']=1.08
df.loc[ix[1],'Activity Status']='Complete'; df.loc[ix[1],'Finish']=pd.NaT
df.loc[ix[2],'BL Finish']=df.loc[ix[2],'BL Start']-pd.Timedelta(days=5)
df.loc[ix[3],'Discipline']=None
df.loc[ix[4],'Activity ID']='A0001'
# Save four raw exports
for dd in data_dates:
 out=df[df['Data Date'].eq(dd)].copy(); out.to_csv(ROOT/f'data/raw/p6_export_{dd:%Y%m%d}.csv',index=False,date_format='%Y-%m-%d')
# clean latest deduplicated/fixed for published analytics
latest_df=df[df['Data Date'].eq(latest)].copy()
latest_df=latest_df.drop_duplicates('Activity ID',keep='first')
latest_df['Discipline']=latest_df['Discipline'].fillna('Unassigned')
latest_df['BL Finish']=latest_df.apply(lambda r: max(r['BL Finish'],r['BL Start']) if pd.notna(r['BL Start']) and pd.notna(r['BL Finish']) else r['BL Finish'],axis=1)
latest_df['Physical % Complete']=latest_df['Physical % Complete'].clip(0,1)
latest_df.to_csv(ROOT/'data/processed/activities_clean.csv',index=False,date_format='%Y-%m-%d')
# weekly curves, weighted by labor units
weeks=pd.date_range(start,finish,freq='W-MON')
curve=[]
for week in weeks:
    plan=[]; real=[]
    for _,r in latest_df.iterrows():
        bs,bf=r['BL Start'],r['BL Finish']; w=r['Budgeted Labor Units']
        p=min(1,max(0,(week-bs).days/max(1,(bf-bs).days)))
        plan.append(p*w)
        # actual interpolated from snapshot if week before data date; otherwise held at latest physical
        progress=r['Physical % Complete'] if week>=latest else min(r['Physical % Complete'], max(0,p*(.94 if r['Discipline']!='Piping' else .86)))
        real.append(progress*w)
    planv=sum(plan)/latest_df['Budgeted Labor Units'].sum(); realv=sum(real)/latest_df['Budgeted Labor Units'].sum()
    curve.append([week,planv,realv])
curve=pd.DataFrame(curve,columns=['Week','Planned Cum %','Actual Cum %'])
# forecast: actual rate recent, extend gap; use max of actual and shifted to close by finish
asof=latest; actual_asof=float(curve.loc[curve.Week<=asof,'Actual Cum %'].iloc[-1]); plan_asof=float(curve.loc[curve.Week<=asof,'Planned Cum %'].iloc[-1])
curve['Forecast Cum %']=curve['Actual Cum %']
future=curve.Week>asof
rate=(actual_asof- float(curve.loc[curve.Week<=asof,'Actual Cum %'].iloc[max(0,len(curve[curve.Week<=asof])-5)]))/5
remaining=max(0,1-actual_asof); n=max(1,future.sum());
curve.loc[future,'Forecast Cum %']=np.minimum(1,actual_asof+remaining*np.cumsum(np.ones(n))/n)
curve.to_csv(ROOT/'data/processed/s_curve_weekly.csv',index=False,date_format='%Y-%m-%d')
# discipline KPIs
k=[]
for disc,g in latest_df.groupby('Discipline',dropna=False):
    weight=g['Budgeted Labor Units'].sum(); real=(g['Budgeted Labor Units']*g['Physical % Complete']).sum()/weight; plan=(g['Budgeted Labor Units']*g.apply(lambda r:min(1,max(0,(latest-r['BL Start']).days/max(1,(r['BL Finish']-r['BL Start']).days))),axis=1)).sum()/weight
    spi=real/plan if plan else np.nan
    late=((g['Physical % Complete']<1) & (g['BL Finish']<latest)).sum()
    k.append([disc,len(g),weight,plan,real,real-plan,spi,int(late)])
kpi=pd.DataFrame(k,columns=['Discipline','Activities','Budgeted Labor Units','Planned %','Actual %','Variance pts','SPI','Late Activities'])
kpi.to_csv(ROOT/'data/processed/kpi_by_discipline.csv',index=False)
# quality checks on raw latest
raw=df[df['Data Date'].eq(latest)].copy(); checks=[]
def chk(name,count,status,action): checks.append({'Control':name,'Issue Count':int(count),'Status':status,'Action':action})
chk('Physical % > 100',(raw['Physical % Complete']>1).sum(),'REVIEW','bloquer la publication et borner après correction')
chk('Completed without Finish',((raw['Activity Status']=='Complete') & raw['Finish'].isna()).sum(),'REVIEW','compléter la date de fin ou repasser en In Progress')
chk('BL Finish before BL Start',(raw['BL Finish']<raw['BL Start']).sum(),'REVIEW','corriger les dates dans P6')
chk('Missing Discipline',raw['Discipline'].isna().sum(),'REVIEW','renseigner la discipline ou affecter Unassigned')
chk('Duplicate Activity ID',raw['Activity ID'].duplicated().sum(),'REVIEW','dédupliquer avant chargement')
chk('Missing Data Date',raw['Data Date'].isna().sum(),'PASS' if raw['Data Date'].isna().sum()==0 else 'REVIEW','rejeter un snapshot sans Data Date')
q=pd.DataFrame(checks); q.to_csv(ROOT/'data/quality/dq_controls.csv',index=False); q.to_json(ROOT/'data/quality/dq_controls.json',orient='records',indent=2)
# charts
plt.style.use('seaborn-v0_8-whitegrid')
fig,ax=plt.subplots(figsize=(11,5)); ax.plot(curve.Week,curve['Planned Cum %']*100,label='Prévu baseline',lw=2); ax.plot(curve.Week,curve['Actual Cum %']*100,label='Réel',lw=2); ax.plot(curve.Week,curve['Forecast Cum %']*100,label='Recalé forecast',lw=2,ls='--'); ax.axvline(asof,color='grey',ls=':'); ax.set_title('Courbe en S — projet industriel'); ax.set_ylabel('Avancement cumulé (%)'); ax.set_ylim(0,105); ax.legend(); fig.tight_layout(); fig.savefig(ROOT/'output/figures/s_curve_project.png',dpi=170); plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5)); x=np.arange(len(kpi)); wbar=.25; ax.bar(x-wbar,kpi['Planned %']*100,wbar,label='Prévu'); ax.bar(x,kpi['Actual %']*100,wbar,label='Réel'); ax.bar(x+wbar,kpi['Variance pts'],wbar,label='Écart (pts)'); ax.set_xticks(x,kpi.Discipline,rotation=20); ax.set_title('KPI par discipline'); ax.set_ylabel('% / points'); ax.legend(); fig.tight_layout(); fig.savefig(ROOT/'output/figures/kpi_disciplines.png',dpi=170); plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5)); order=kpi.sort_values('SPI'); colors=['#c0392b' if z<.9 else '#f39c12' if z<1 else '#2e86c1' for z in order.SPI]; ax.barh(order.Discipline,order.SPI,color=colors); ax.axvline(1,color='black',ls='--'); ax.set_title('SPI par discipline'); ax.set_xlabel('SPI = réel / prévu'); fig.tight_layout(); fig.savefig(ROOT/'output/figures/spi_disciplines.png',dpi=170); plt.close(fig)
# Excel workbook
wb=Workbook(); ws=wb.active; ws.title='Import'
for name,data in [('Import',raw),('Contrôles',q),('Données propres',latest_df),('KPI discipline',kpi),('Courbe S',curve)]:
    if name!='Import': ws2=wb.create_sheet(name)
    else: ws2=ws
    ws2.append(list(data.columns))
    for row in data.itertuples(index=False,name=None): ws2.append([None if pd.isna(v) else v.to_pydatetime() if isinstance(v,pd.Timestamp) else v for v in row])
    for cell in ws2[1]: cell.font=Font(bold=True,color='FFFFFF'); cell.fill=PatternFill('solid',fgColor='1F4E78'); cell.alignment=Alignment(horizontal='center')
    ws2.freeze_panes='A2'; ws2.auto_filter.ref=ws2.dimensions
    for col in range(1,ws2.max_column+1): ws2.column_dimensions[get_column_letter(col)].width=min(28,max(12,max(len(str(ws2.cell(row=r,column=col).value or '')) for r in range(1,min(ws2.max_row,50)+1))+2))
# add charts
chart=LineChart(); chart.title='Courbe en S'; chart.y_axis.title='Avancement %'; chart.x_axis.title='Semaine'; chart.add_data(Reference(wb['Courbe S'],min_col=2,max_col=4,min_row=1,max_row=wb['Courbe S'].max_row),titles_from_data=True); chart.set_categories(Reference(wb['Courbe S'],min_col=1,min_row=2,max_row=wb['Courbe S'].max_row)); wb['Courbe S'].add_chart(chart,'F2')
bar=BarChart(); bar.title='SPI par discipline'; bar.add_data(Reference(wb['KPI discipline'],min_col=7,min_row=1,max_row=wb['KPI discipline'].max_row),titles_from_data=True); bar.set_categories(Reference(wb['KPI discipline'],min_col=1,min_row=2,max_row=wb['KPI discipline'].max_row)); wb['KPI discipline'].add_chart(bar,'J2')
wb.save(ROOT/'excel/project_progress_reporting.xlsx')
# summary
summary={'activities_raw':300,'activities_clean':len(latest_df),'disciplines':int(latest_df.Discipline.nunique()),'areas':int(latest_df.Area.nunique()),'snapshots':4,'data_date':str(latest.date()),'planned_pct':round(plan_asof*100,1),'actual_pct':round(actual_asof*100,1),'variance_pts':round((actual_asof-plan_asof)*100,1),'spi':round(actual_asof/plan_asof,3),'quality_controls':len(q),'quality_issues':int((q['Status']=='REVIEW').sum()),'workbook_sheets':5}
(ROOT/'output/summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
print(summary)

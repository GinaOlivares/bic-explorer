"""BIC Explorer: generic interactive electromagnetic research laboratory."""
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from bic_explorer.physics.core import Guide, cutoff, beta, fields, channels, coax, parity, overlap, cmt, quasi

st.set_page_config(page_title='BIC Explorer', page_icon='◈', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container{max-width:1450px;padding-top:2.2rem;padding-bottom:4rem} h1,h2,h3{letter-spacing:-.025em} h1{font-weight:650} [data-testid="stSidebar"]{border-right:1px solid #263541} .eyebrow{color:#56d9d0;text-transform:uppercase;letter-spacing:.18em;font-size:.72rem;font-weight:700}.lead{font-size:1.12rem;color:#b8c9d1;max-width:850px;line-height:1.7}.rule{border-top:1px solid #263541;margin:1.5rem 0}.tag{display:inline-block;color:#6ce0d4;border:1px solid #315c60;border-radius:4px;padding:.25rem .55rem;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase}
</style>''',unsafe_allow_html=True)
PAGES=['Research Overview','Electromagnetic Geometry','Waveguide Mode Explorer','Propagation Channels','TEM Explorer','Symmetry Explorer','Coupled Mode Theory Lab','BIC & Quasi-BIC Simulator','Research Roadmap','References & Limitations']
with st.sidebar:
    st.markdown('<div class="eyebrow">Interactive research lab</div>',unsafe_allow_html=True)
    st.title('BIC Explorer')
    st.caption('Electromagnetic theory · open systems')
    page=st.radio('Navigate',PAGES,label_visibility='collapsed',key='navigation')
    st.markdown('---')
    st.caption('MODEL STATUS · Generic & synthetic')
    if st.button('Reset all controls',use_container_width=True):
        for key in list(st.session_state): del st.session_state[key]
        st.rerun()
    st.caption('No unpublished device data are used.')

def header(k,title,desc,label):
    st.markdown(f'<div class="eyebrow">{k} / BIC Explorer</div>',unsafe_allow_html=True)
    st.title(title); st.markdown(f'<p class="lead">{desc}</p>',unsafe_allow_html=True)
    st.markdown(f'<span class="tag">{label}</span><div class="rule"></div>',unsafe_allow_html=True)
def plot(fig):
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#101c25',font=dict(color='#dbe9ed',family='Arial'),margin=dict(l=10,r=15,t=40,b=10),legend=dict(orientation='h',y=1.12))
    st.plotly_chart(fig,use_container_width=True)
def guide_controls(prefix):
    a,b,c,d=st.columns(4)
    w=a.number_input('Width w (mm)',5.,100.,30.,1.,key=prefix+'w'); h=b.number_input('Height h (mm)',5.,100.,15.,1.,key=prefix+'h')
    er=c.number_input('Relative permittivity εᵣ',.1,20.,1.,.1,key=prefix+'er'); mr=d.number_input('Relative permeability μᵣ',.1,10.,1.,.1,key=prefix+'mr')
    return Guide(w/1000,h/1000,er,mr)
def line(x,y,name,**kw): return go.Scatter(x=x,y=y,name=name,mode='lines',**kw)
def download(df,meta,name):
    data='# '+json.dumps(meta,sort_keys=True)+'\n'+df.to_csv(index=False)
    st.download_button('Download calculated CSV',data,name,'text/csv')

if page==PAGES[0]:
    header('01','Research Overview','A laboratory for exploring how guided waves, symmetry and open channels shape bound states in the continuum.','Theory / generic examples')
    a,b=st.columns([1.5,1],gap='large')
    with a:
        st.subheader('An eigenstate inside the continuum')
        st.write('A bound state in the continuum (BIC) is a localized eigenstate whose frequency lies among propagating channels, yet which radiates into none of them in an ideal lossless system. Its existence requires an eigenstate and cancellation or exclusion of all open-channel leakage.')
        st.write('An ordinary bound state below cutoff lies outside the propagating continuum. A quasi-BIC leaks weakly and has a finite radiative lifetime. A driven scattering feature is a response to excitation and is not, by itself, proof of an eigenstate. Intrinsic loss can limit lifetime even when radiation vanishes.')
        st.info('All examples are generic or synthetic. No unpublished findings, device details or experimental results are disclosed. This app does not demonstrate a BIC in the research system.')
    with b:
        st.subheader('Explore the physics')
        st.markdown('**01** · Inspect a generic guide geometry  \n**02** · Calculate analytical modes and open channels  \n**03** · Examine parity and channel coupling  \n**04** · Explore a synthetic two-resonance model  \n**05** · Study quasi-BIC linewidth and lifetime')
        st.markdown('---'); st.caption('2026 postdoctoral project · Instituto de Física, Universidad Autónoma de San Luis Potosí · Dr. Georgina Angélica Olivares Rentería')
elif page==PAGES[1]:
    header('02','Electromagnetic Geometry','Inspect a generic rectangular guide and its coordinate system.','Conceptual schematic')
    a,b,c=st.columns(3); w=a.slider('Width (mm)',10,80,30); h=b.slider('Height (mm)',5,50,15); L=c.slider('Length (mm)',30,200,90)
    inclusion=st.checkbox('Show schematic dielectric inclusion'); planes=st.checkbox('Show cross-sectional plane',True); axes=st.checkbox('Show coordinate axes',True)
    fig=go.Figure()
    for yy in [-w/2,w/2]:
        for zz in [0,h]: fig.add_trace(go.Scatter3d(x=[0,L],y=[yy,yy],z=[zz,zz],mode='lines',line=dict(color='#63d6cf',width=5),showlegend=False))
    for xx in [0,L]:
        for yy in [-w/2,w/2]: fig.add_trace(go.Scatter3d(x=[xx,xx],y=[yy,yy],z=[0,h],mode='lines',line=dict(color='#63d6cf',width=5),showlegend=False))
        for zz in [0,h]: fig.add_trace(go.Scatter3d(x=[xx,xx],y=[-w/2,w/2],z=[zz,zz],mode='lines',line=dict(color='#63d6cf',width=5),showlegend=False))
    if planes: fig.add_trace(go.Mesh3d(x=[L/2]*4,y=[-w/2,w/2,w/2,-w/2],z=[0,0,h,h],i=[0,0],j=[1,2],k=[2,3],color='#68c8d5',opacity=.18,name='Cross section'))
    if inclusion:
        fig.add_trace(go.Mesh3d(x=[L*.4,L*.6,L*.6,L*.4,L*.4,L*.6,L*.6,L*.4],y=[-w*.15,-w*.15,w*.15,w*.15]*2,z=[h*.25]*4+[h*.75]*4, alphahull=0,color='#e9b873',opacity=.65,name='Schematic inclusion'))
        st.warning('The inclusion is schematic only. Its fields are not solved and it does not change the empty-guide analytical solver.')
    if axes:
        for x,y,z,name,col in [([0,L*.25],[0,0],[0,0],'x','#ff8d88'),([0,0],[0,w*.4],[0,0],'y','#8ae3bd'),([0,0],[0,0],[0,h*.8],'z','#b4a4ff')]: fig.add_trace(go.Scatter3d(x=x,y=y,z=z,mode='lines+text',text=['',name],line=dict(color=col,width=7),showlegend=False))
    fig.update_layout(scene=dict(xaxis_title='x (mm)',yaxis_title='y (mm)',zaxis_title='z (mm)',aspectmode='data'),height=570); plot(fig)
    st.caption(f'Cross section: y ∈ [−{w/2:g}, {w/2:g}] mm; z ∈ [0, {h:g}] mm. Propagation is along x.')
    f=go.Figure(go.Scatter(x=[-w/2,w/2,w/2,-w/2,-w/2],y=[0,0,h,h,0],fill='toself',fillcolor='rgba(86,217,208,.1)',line_color='#56d9d0')); f.update_layout(xaxis_title='y (mm)',yaxis_title='z (mm)',height=300,yaxis_scaleanchor='x'); plot(f)
elif page==PAGES[2]:
    header('03','Waveguide Mode Explorer','Analytical fields in a homogeneous, perfectly conducting rectangular guide.','Analytical textbook model')
    g=guide_controls('mode'); a,b,c,d=st.columns(4); kind=a.selectbox('Mode family',['TE','TM']); m=b.number_input('Index m',0 if kind=='TE' else 1,5,1); n=c.number_input('Index n',0 if kind=='TE' else 1,5,0 if kind=='TE' else 1); f=d.number_input('Frequency (GHz)',.1,100.,12.,.1)*1e9
    if kind=='TE' and m==n==0: st.error('TE00 is not a valid mode.'); st.stop()
    fc=cutoff(g,kind,m,n); bt=beta(g,kind,m,n,f)
    st.metric('Cutoff frequency',f'{fc/1e9:.4f} GHz',f'{"propagating" if bt.real else "evanescent" if bt.imag else "at cutoff"}')
    st.caption('Convention: exp(iβx − iωt); β has nonnegative imaginary part. E and H are independently normalized and cannot be compared as energy.')
    c1,c2,c3=st.columns(3); component=c1.selectbox('Component',['Ex','Ey','Ez','Hx','Hy','Hz']); view=c2.selectbox('View',['Magnitude','Real','Imaginary']); phase=c3.slider('Phase (degrees)',0,360,0)
    y=np.linspace(-g.w/2,g.w/2,101); z=np.linspace(0,g.h,81); Y,Z=np.meshgrid(y,z); E,H=fields(g,kind,m,n,f,Y,Z); F=E if component[0]=='E' else H; scale=max(np.max(np.abs(v)) for v in F); scale=scale or 1; val=F['xyz'.index(component[1])]/scale*np.exp(-1j*np.deg2rad(phase)); data=abs(val) if view=='Magnitude' else val.real if view=='Real' else val.imag
    fig=go.Figure(go.Heatmap(x=y*1e3,y=z*1e3,z=data,colorscale='Viridis' if view=='Magnitude' else 'RdBu',colorbar_title='Normalized')); fig.update_layout(xaxis_title='y (mm)',yaxis_title='z (mm)',height=480); plot(fig)
    if st.checkbox('Show transverse vector arrows'):
        fig=go.Figure(); sy=Y[::10,::10]*1e3; sz=Z[::10,::10]*1e3; vy=(F[1]/scale*np.exp(-1j*np.deg2rad(phase))).real[::10,::10]; vz=(F[2]/scale*np.exp(-1j*np.deg2rad(phase))).real[::10,::10]
        for yy,zz,dy,dz in zip(sy.flat,sz.flat,vy.flat,vz.flat): fig.add_annotation(x=yy+dy*g.w*100,y=zz+dz*g.h*100,ax=yy,ay=zz,xref='x',yref='y',axref='x',ayref='y',showarrow=True,arrowhead=2,arrowcolor='#58d8cf')
        fig.update_layout(xaxis=dict(title='y (mm)',range=[-g.w*550,g.w*550]),yaxis=dict(title='z (mm)',range=[-g.h*50,g.h*1050]),height=400); plot(fig)
    if st.checkbox('Show longitudinal slice'):
        xx=np.linspace(0,.2,250); e,h=fields(g,kind,m,n,f,0,g.h/2,xx); v=(e if component[0]=='E' else h)['xyz'.index(component[1])]/scale; fig=go.Figure(line(xx*1000,abs(v),'Magnitude')); fig.update_layout(xaxis_title='x (mm)',yaxis_title='Normalized magnitude'); plot(fig); st.caption('At this cross-section point; evanescent modes decay in +x.')
    with st.expander('Equations and assumptions'):
        st.latex(r'k_c^2=(m\pi/w)^2+(n\pi/h)^2,\quad \beta=\sqrt{\omega^2\mu\epsilon-k_c^2}')
        st.write('TE: Hₓ = H₀ cos(mπu/w) cos(nπz/h). TM: Eₓ = E₀ sin(mπu/w) sin(nπz/h), u = y + w/2. Transverse fields follow from Maxwell’s curl equations. This is an empty homogeneous guide, not a loaded resonator.')
    download(pd.DataFrame({'y_mm':Y.ravel()*1e3,'z_mm':Z.ravel()*1e3,'normalized_value':data.ravel()}),{'model':'analytical empty guide','mode':f'{kind}{m}{n}','frequency_Hz':f,'w_m':g.w,'h_m':g.h,'epsilon_r':g.er,'mu_r':g.mr,'component':component,'view':view,'phase_degrees':phase},'guide_field.csv')
elif page==PAGES[3]:
    header('04','Propagation Channels','Cutoff, dispersion and the set of available guide modes.','Analytical textbook model')
    g=guide_controls('channel'); a,b=st.columns(2); f=a.slider('Frequency (GHz)',1.,80.,12.,.5)*1e9; limit=b.slider('Maximum mode index',1,5,2)
    rows=channels(g,limit,f); df=pd.DataFrame(rows); st.dataframe(df.rename(columns={'fc_GHz':'Cutoff (GHz)','beta_per_m':'β (rad/m)','alpha_per_m':'α (1/m)'}),hide_index=True,use_container_width=True)
    st.caption('List truncated at the selected indices. Cutoff tolerance: |k² − k꜀²| ≤ 10⁻¹² max(k², k꜀²). Undefined values are blank; a port excitation is not the full set of open channels.')
    fig=go.Figure(); ff=np.linspace(.1,80,300)
    for r in rows[:min(len(rows),12)]:
        fc=r['fc_GHz']; bv=2*np.pi*ff*1e9*np.sqrt(g.mu*g.eps)*np.sqrt(np.maximum(0,1-(fc/ff)**2)); bv[ff<fc]=np.nan
        fig.add_trace(line(bv,ff,r['mode'])); fig.add_trace(go.Scatter(x=[0],y=[fc],mode='markers',showlegend=False,marker=dict(size=5,color='#56d9d0')))
    fig.update_layout(xaxis_title='β (rad/m)',yaxis_title='Frequency (GHz)',height=500); plot(fig)
    st.write('For propagating modes, vₚv𝗀 = 1/(με). At cutoff the guided wavelength and phase velocity diverge; evanescent modes instead have a finite amplitude decay length.')
    download(df,{'model':'analytical empty guide','frequency_Hz':f,'maximum_index':limit,'guide':g.__dict__},'channels.csv')
elif page==PAGES[4]:
    header('05','TEM Explorer','Ideal homogeneous coaxial line, independent of any research feed.','Analytical textbook model')
    a,b,c,d,e=st.columns(5); aa=a.number_input('Inner radius a (mm)',.1,30.,2.); bb=b.number_input('Outer radius b (mm)',.2,50.,8.); er=c.number_input('εᵣ',.1,20.,1.); mr=d.number_input('μᵣ',.1,10.,1.); V=e.number_input('Voltage amplitude (V)',.1,100.,1.)
    if aa>=bb: st.error('The outer radius must exceed the inner radius.'); st.stop()
    x=np.linspace(-bb,bb,151); X,Y=np.meshgrid(x,x); R=np.hypot(X,Y); E,H,Z=coax(aa/1000,bb/1000,er,mr,V,R/1000)
    st.metric('Characteristic impedance',f'{Z:.2f} Ω'); st.caption('Eᵣ = V/[r ln(b/a)], Hφ = Eᵣ/η for +z propagation. No cutoff exists for the ideal TEM mode; higher coaxial modes are not computed.')
    fig=go.Figure(go.Heatmap(x=x,y=x,z=E,colorscale='Viridis',colorbar_title='Eᵣ (V/m)')); fig.update_layout(xaxis_title='x (mm)',yaxis_title='y (mm)',yaxis_scaleanchor='x',height=480); plot(fig)
    rr=np.linspace(aa,bb,300); ee,hh,_=coax(aa/1000,bb/1000,er,mr,V,rr/1000); fig=go.Figure(line(rr,ee,'Eᵣ (V/m)')); fig.update_layout(xaxis_title='Radius (mm)',yaxis_title='Eᵣ (V/m)'); plot(fig)
    download(pd.DataFrame({'radius_mm':rr,'E_V_per_m':ee,'H_A_per_m':hh}),{'model':'ideal coax TEM','a_mm':aa,'b_mm':bb,'epsilon_r':er,'mu_r':mr,'V':V},'tem_profile.csv')
elif page==PAGES[5]:
    header('06','Symmetry Explorer','Parity and overlap on a symmetric interval.','Conceptual symmetry illustration')
    mix=st.slider('Odd perturbation amplitude',-2.,2.,0.,.05); y=np.linspace(-1,1,1001); even=np.cos(np.pi*y/2); odd=np.sin(np.pi*y); f=even+mix*odd; ev,od=parity(y,f)
    fig=go.Figure([line(y,f,'Mixed function'),line(y,f[::-1],'Mirror f(−y)',line=dict(dash='dash')),line(y,ev,'Even part'),line(y,od,'Odd part')]); fig.update_layout(xaxis_title='Normalized transverse coordinate',yaxis_title='Amplitude'); plot(fig)
    st.metric('Normalized overlap: even basis with mixed function',f'{overlap(y,even,f):.5f}'); st.write(f'Even–odd basis overlap: {overlap(y,even,odd):.2e}. The decomposition uses fₑ = [f(y)+f(−y)]/2 and fₒ = [f(y)−f(−y)]/2.')
    st.warning('Scalar component parity is not the full vector transformation: E is polar and H is axial under a mirror. A zero overlap alone does not establish a BIC or a device-specific selection rule.')
elif page==PAGES[6]:
    header('07','Coupled Mode Theory Lab','Two synthetic resonances coupled to one or two open channels.','Synthetic reduced-order model')
    preset=st.selectbox('Preset',['Dark antisymmetric state','Detuned resonances','Second channel open','Intrinsic loss','Custom'])
    presets={'Dark antisymmetric state':(1.,1.,.08,.25,.25,0.,0.),'Detuned resonances':(.9,1.1,.08,.25,.25,0.,0.),'Second channel open':(1.,1.,.08,.25,.25,.15,0.),'Intrinsic loss':(1.,1.,.08,.25,.25,0.,.03),'Custom':(1.,1.,.08,.25,.25,0.,0.)}; p=presets[preset]
    a,b,c,d=st.columns(4); w1=a.number_input('ω₁',.1,3.,p[0],.01,key='w1'+preset); w2=b.number_input('ω₂',.1,3.,p[1],.01,key='w2'+preset); J=c.number_input('J',-.5,.5,p[2],.01,key='j'+preset); loss=d.number_input('Intrinsic loss γᵢ',0.,1.,p[6],.01,key='loss'+preset)
    a,b,c=st.columns(3); wa=a.number_input('Channel 1 coupling, mode 1',-.8,.8,p[3],.01,key='wa'+preset); wb=b.number_input('Channel 1 coupling, mode 2',-.8,.8,p[4],.01,key='wb'+preset); wc=c.number_input('Independent channel strength',0.,.8,p[5],.01,key='wc'+preset)
    W=np.array([[wa,wc],[wb,-wc]]) if wc else np.array([[wa],[wb]]); H,states=cmt(w1,w2,J,W,[loss,loss]); fig=go.Figure(go.Scatter(x=[s['value'].real for s in states],y=[s['value'].imag for s in states],mode='markers+text',text=['State 1','State 2'],textposition='top center',marker=dict(size=14,color=['#56d9d0','#efb86e']))); fig.update_layout(xaxis_title='Re λ (normalized frequency)',yaxis_title='Im λ (normalized frequency)',height=400); plot(fig)
    for i,s in enumerate(states):
        q=s['value'].real/s['width'] if s['width']>1e-12 and s['value'].real>0 else np.inf
        st.write(f"**State {i+1}** · λ = {s['value'].real:.5f} {s['value'].imag:+.5f}i · γrad = {s['rad']:.5g} · γint = {s['intr']:.5g} · Q = {q:.5g} · residual = {s['residual']:.2e}")
        st.caption(f"Eigenvector: [{s['vector'][0]:.3g}, {s['vector'][1]:.3g}]; channel leakage |W†v|²: {np.abs(W.T@s['vector'])**2}; " + ('lossless BIC candidate within assumed continuum' if s['candidate'] else 'not a lossless BIC candidate'))
    st.write('Hₑff = H₀ − i(WW† + Γᵢ)/2; exp(−iωt). The positive-frequency continuum is assumed in this toy model. A null coupling vector must also be an eigenvector, with no intrinsic loss, to qualify as a candidate. No scattering spectrum is inferred.')
    if abs(states[0]['value']-states[1]['value'])<1e-7: st.warning('Near degeneracy: eigenvector identities can be ambiguous.')
elif page==PAGES[7]:
    header('08','BIC & Quasi-BIC Simulator','Explore local quadratic radiation leakage and energy ringdown.','Synthetic reduced-order model')
    a,b,c,d=st.columns(4); delta=a.slider('Signed perturbation δ',-1.,1.,.1,.01); A=b.number_input('Radiation coefficient A',.001,5.,.2,.01); omega=c.number_input('Frequency ω₀',.1,10.,1.,.1); loss=d.number_input('Intrinsic linewidth γᵢ',0.,2.,.01,.01)
    rad,total,qr,qt=quasi(delta,A,omega,loss); m1,m2,m3=st.columns(3); m1.metric('Radiative linewidth',f'{rad:.4g}'); m2.metric('Radiative Q','∞' if np.isinf(qr) else f'{qr:.4g}'); m3.metric('Total Q','∞' if np.isinf(qt) else f'{qt:.4g}')
    ds=np.logspace(-3,0,200); r,t,q,qq=quasi(ds,A,omega,loss); fig=go.Figure([line(ds,r,'γ radiation'),line(ds,t,'γ total'),line(ds,A*ds**2,'slope 2 guide',line=dict(dash='dash'))]); fig.update_layout(xaxis_type='log',yaxis_type='log',xaxis_title='|δ| (zero excluded)',yaxis_title='Linewidth (normalized)'); plot(fig)
    fig=go.Figure([line(ds,q,'Q radiation'),line(ds,qq,'Q total')]); fig.update_layout(xaxis_type='log',yaxis_type='log',xaxis_title='|δ| (zero excluded)',yaxis_title='Quality factor Q'); plot(fig)
    end=10/float(total) if total>0 else 100; time=np.linspace(0,end,300); fig=go.Figure(line(time,np.exp(-float(total)*time),'Energy')); fig.update_layout(xaxis_title='Time (inverse normalized frequency)',yaxis_title='U(t) / U(0)',yaxis_range=[0,1.05]); plot(fig)
    st.caption('At δ = 0 radiative linewidth is exactly zero and radiative Q is infinite; zero is omitted from logarithmic axes. This leading-order quadratic law is illustrative, not universal. Intrinsic loss limits total Q. A quasi-BIC has weak leakage; an ordinary resonance need not follow this scaling.')
    download(pd.DataFrame({'abs_delta':ds,'gamma_rad':r,'gamma_total':t,'Q_rad':q,'Q_total':qq}),{'model':'synthetic local quadratic scaling','A':A,'omega0':omega,'intrinsic_loss':loss},'quasibic.csv')
elif page==PAGES[8]:
    header('09','Research Roadmap','A public-safe view of the methodological workflow for the 2026 postdoctoral project.','Research progress / public metadata')
    with open('metadata.json',encoding='utf-8') as file: meta=json.load(file)
    for i,step in enumerate(meta['workflow']): st.markdown(f"**{i+1:02d}  {step}**" + ('  →' if i<len(meta['workflow'])-1 else ''))
    st.markdown('---')
    for item in meta['status']: st.write(f"**{item['activity']}** · {item['status']}")
    st.info('Manuscript in preparation; detailed findings are withheld pending publication. Device-specific eigenproblem and validation remain ongoing or pending confirmation. No experimental validation is claimed.')
    st.caption('Physics of Waves and Electromagnetism research line · Perfect absorption is a possible future-related topic, not a claimed result.')
else:
    header('10','References & Limitations','Sources and interpretation boundaries for the models in this laboratory.','Documentation')
    st.markdown('''- Hsu, C. W., Zhen, B., Stone, A. D., Joannopoulos, J. D. & Soljačić, M. “Bound states in the continuum.” *Nature Reviews Materials* **1**, 16048 (2016). [DOI: 10.1038/natrevmats.2016.48](https://doi.org/10.1038/natrevmats.2016.48).
- Fan, S., Suh, W. & Joannopoulos, J. D. “Temporal coupled-mode theory for the Fano resonance in optical resonators.” *Journal of the Optical Society of America A* **20**, 569–572 (2003). [DOI: 10.1364/JOSAA.20.000569](https://doi.org/10.1364/JOSAA.20.000569).
- Ellingson, S. W. [Rectangular waveguide TE modes](https://phys.libretexts.org/Bookshelves/Electricity_and_Magnetism/Electromagnetics_II_(Ellingson)/06%3A_Waveguides/6.09%3A_Rectangular_Waveguide-_TE_Modes), *Electromagnetics II*, LibreTexts.''')
    st.subheader('Glossary')
    st.write('**Open channel** — a propagating radiation or guide mode. **Cutoff** — the threshold between propagating and evanescent guide behavior. **Linewidth γ** — energy decay rate in the normalized CMT convention. **Q** — frequency divided by energy linewidth. **Quasi-BIC** — a weakly radiating resonance near an ideal BIC.')
    st.subheader('Model boundaries')
    st.write('Guide and coax calculations assume ideal conductors and homogeneous, isotropic, nondispersive, lossless media. The inclusion is schematic. Symmetry uses scalar test functions. CMT and quadratic leakage are synthetic reduced-order models with an assumed continuum; they do not solve a device eigenproblem. No experimental or full-wave data are included.')

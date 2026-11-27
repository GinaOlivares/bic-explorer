from streamlit.testing.v1 import AppTest

def test_navigation_and_widgets():
 at=AppTest.from_file('app.py',default_timeout=30).run()
 assert not at.exception
 for page in ['Electromagnetic Geometry','Waveguide Mode Explorer','Propagation Channels','TEM Explorer','Symmetry Explorer','Coupled Mode Theory Lab','BIC & Quasi-BIC Simulator','Research Roadmap','References & Limitations','Research Overview']:
  at.sidebar.radio[0].set_value(page).run()
  assert not at.exception, (page,at.exception)
 at.sidebar.button[0].click().run(); assert not at.exception

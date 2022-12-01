import base64
from io import StringIO
import streamlit as st
import pandas as pd
import numpy as np

from utilities import *


st.title("ASACI TECHNOLOGIES : INTERFACE DE VALIDATION <FICHIERS D'EDITION D'ATTESTATION>")

fichier = st.file_uploader("Choisir un fichier EXCEL", type=["xlsx", "xls"])


if fichier is not None:

    details = {"filename":fichier.name, "filetype":fichier.type, "filesize":fichier.size}
			
    st.write(details)

    #data = pd.read_excel(fichier, sheet_name="demande")
    data = pd.read_excel(fichier)
    
    st.write(data.head(10))
    
    columns = data.columns
    difcols = [c for c in COLUMNS if c not in columns]
    
    data = data[COLUMNS]
    
    validation, messages = False, []
    if len(difcols) == 0:
        compagnies = data['code_compagnie'].unique().tolist()
        if len(compagnies) == 1:
            rows = data.to_dict(orient='records')
            for i, row in enumerate(rows):
                vi, mi = control_row(i-1,row)
                #st.write('--------------------------------------------')
                #if vi: st.write(f'Ligne {i+1} ')
                if not vi: 
                    st.write('--------------------------------------------')
                    st.write(mi)
        else:
            st.write('Le code compagnie doit etre unique')
    else:
        st.write(f'Toutes les colonnes ne sont pas presentes,\n Il manque {difcols}')
    
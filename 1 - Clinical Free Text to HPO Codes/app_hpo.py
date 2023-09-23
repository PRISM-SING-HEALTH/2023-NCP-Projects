"""
Created on Mon Jan 30 2023
Code included from: Phenotagger Demo: https://huggingface.co/spaces/lingbionlp/PhenoTaggger-Demo
                    PhenoBERT: https://github.com/EclipseCN/PhenoBERT
"""
import streamlit as st
import sys
sys.path.append("huggingface_phenotagger")
from src.nn_model import bioTag_CNN,bioTag_Bioformer
from src.dic_ner import dic_ont
from src.tagging_text import bioTag
from pandas import DataFrame, concat
import nltk 
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
sys.path.append("PHENOBERT/phenobert/utils")
from api import annotate_text
import requests

st.set_page_config(
    page_title="Clinical Free Text to HPO Code",
    layout="wide", )

# initalize required values in session state
if 'url' not in st.session_state:
    st.session_state.url = "https://hpo.jax.org/api/hpo/search"
if 'known' not in st.session_state:
    st.session_state.known = []
if 'rerun' not in st.session_state:
    st.session_state.rerun = -1
if 'prev_button' not in st.session_state:
    st.session_state.prev_button = False
if 'prev_df_sel_rows' not in st.session_state:
    st.session_state.prev_df_sel_rows = DataFrame()
if 'df' not in st.session_state:
    st.session_state.df = DataFrame(columns=["HPO ID", "Given Term", "Official Term"]).reset_index(drop=True)
if 'prev_df' not in st.session_state:
    st.session_state.prev_df = DataFrame(columns=["HPO ID", "Given Term", "Official Term"]).reset_index(drop=True) 
if 'prev_selec' not in st.session_state:
    st.session_state.prev_selec = []
if 'changed' not in st.session_state:
    st.session_state.changed = False
if 'button' not in st.session_state:
    st.session_state.button = False

@st.experimental_memo
def convert_df_to_csv(df):
    return df.to_csv().encode('utf-8')

@st.experimental_memo
def convert_df_to_json(df):
    return df.to_json(orient="columns")

@st.experimental_memo
def convert_df_to_string(df):
    return df.to_string()

@st.experimental_memo
def data_upload(data_entity):
    df = DataFrame(data_entity, columns=["HPO ID", "Given Term", "Official Term"]).reset_index(drop=True)
    return df  

def generate_aggrid(df, pre_row=None, key=None, checkbox=True, reload=False ):
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(editable=True, groupable=True)
    gd.configure_column(field='HPO ID', headerCheckboxSelection=True)
    gd.configure_selection(selection_mode="multiple", use_checkbox=checkbox, pre_selected_rows=pre_row)
    gridoptions = gd.build() 
    grid_table = AgGrid(
    df,
    gridOptions=gridoptions,
    fit_columns_on_grid_load=True,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    theme="streamlit",
    key = key,
    reload_data=reload) 
    return grid_table

# javascript code for cell renderer of 'present' column in generate_aggrid_final
cellRend_1 = JsCode('''
    function(params) {
        let operatorValue = params.value;
        const input = document.createElement('input');
        input.type = 'checkbox';
        if (operatorValue) {
            input.checked = true;
            params.data.present = true;
        } else {
            input.checked = false;
            params.data.present = false;
        }
        input.addEventListener('click', function (event) {
          input.checked != input.checked;
          params.data.present  = input.checked;
          params.setValue(input.checked);
        });
    return input;
    }''')
# javascript code for cell renderer of 'absent' column in generate_aggrid_final
cellRend_2 = JsCode('''
    function(params) {
        let operatorValue = params.value;
        const input = document.createElement('input');
        input.type = 'checkbox';
        if (operatorValue) {
            input.checked = true;
            params.data.absent = true;
        } else {
            input.checked = false;
            params.data.absent = false;
        }
        input.addEventListener('click', function (event) {
          input.checked != input.checked;
          params.data.absent  = input.checked;
          params.setValue(input.checked);
        });
    return input;
    }''')
# javascript code for cell renderer of 'notRelevant' column in generate_aggrid_final
cellRend_3 = JsCode('''
    function(params) {
        let operatorValue = params.value;
        const input = document.createElement('input');
        input.type = 'checkbox';
        if (operatorValue) {
            input.checked = true;
            params.data.notRelevant = true;
        } else {
            input.checked = false;
            params.data.notRelevant = false;
        }
        input.addEventListener('click', function (event) {
          input.checked != input.checked;
          params.data.notRelevant  = input.checked;
          params.setValue(input.checked);
        });
    return input;
    }''')

def generate_aggrid_final(df, cellRend1, cellRend2, cellRend3):
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(editable=True, groupable=True)
    gd.configure_column(field='HPO ID', headerCheckboxSelection=True)
    gd.configure_selection(selection_mode="multiple", use_checkbox=True)
    grid_options = gd.build()
    grid_options['columnDefs'].extend([{
    'field': 'present',
    'header': 'Present',
    'cellRenderer': cellRend_1,

    },
    {
    'field': 'absent',
    'header': 'Absent',
    'cellRenderer': cellRend_2,
    },
    {
    'field': 'notRelevant',
    'header':'Not Relevant',
    'cellRenderer':cellRend_3,
    }]) 
    grid_table = AgGrid(
    df,
    gridOptions=grid_options,
    fit_columns_on_grid_load=False,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    theme="streamlit",
    allow_unsafe_jscode = True,
    )
    return grid_table 

@st.experimental_memo
def api_call(term, results_shown):
    """
    Function handles API request to HPO API.

    :param term: clinical term that user wants associated HPO code for
    :return: None
    """
    res = [] 
    try:
        r = requests.get(st.session_state.url, params={'q':term}, timeout=15)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err_h:
        print ("Http Error:",err_h)
    except requests.exceptions.ConnectionError as err_c:
        print ("Error Connecting:",err_c)
    except requests.exceptions.Timeout as err_t:
        print ("Timeout Error:",err_t)
    except requests.exceptions.RequestException as err:
        print ("Error: Something Else",err)
    data = r.json()
    length =  len(data['terms'])
    if length > 0:
        # restrict to top results for each phenotype according to user choices of 3, 8, and all
        if results_shown == 'Three (3)':
            if length > 3:
                data['terms'] = data['terms'][:3] 
        elif results_shown == 'Eight (8)':
            if length > 8:
                data['terms'] = data['terms'][:8]
        for j in data['terms']:
            name = j['name']
            hpo =j['id']
            res += [[hpo, term, name]]
    else:
        st.write('Cannot find associated HPO code for' + ' "' + term.strip() + '"' + '.')
    return res


def res_max_change():
    # set session_state_changed true if user changes number or results to be shown for the search bar
    st.session_state.changed = True

def clear():
     # allow reruns with new data
    for k in st.session_state:
        del st.session_state[k]
    st.experimental_memo.clear()

@st.experimental_memo
def data_entity(_res_phen, res_phentag):
    """
    Organise phenotagger and phenobert annotations into same format to convert to dataframe.

    :param _res_phen: phenobert tags. The underscore indicates it is an unhashable parameter for st.experimental_memo
    :param _res_phentag: phenotagger tags.    
    :return: Returns organised format for both sets of tags
    """
    data_entity_phenobert = []
    term = ''
    for tag in _res_phen:
        for item in tag[0].word_items:
            term += item.text + ' '
        data_entity_phenobert.append([tag[1], term.strip('\n'), tag[-2]])
        term = ''
    data_entity_phenotagger = []
    for tag in res_phentag:
        data_entity_phenotagger.append([tag[2], doc[(int(tag[0])-1):(int(tag[1]))].strip('\n'), biotag_dic.hpo_word[tag[2]][0]])
    return data_entity_phenobert, data_entity_phenotagger

@st.experimental_memo
def highlight(doc):
    # highlight phenotypes in text
    list_doc = list(doc)
    all_phenotypes = st.session_state.tag_result_phenotagger + st.session_state.tag_result_phenobert 
    for tag in all_phenotypes:
        if tag[-1] == 'orange':
            start = tag[0].start_loc 
            end = tag[0].end_loc -1
            entity_id = tag[1]
            html_tag_start = '<font style="text-decoration: orange dashed underline 3px;" title="'+entity_id+'">'
            html_tag_end = '</font>'
        elif tag[-1] == 'yellow':
            start = int(tag[0]) 
            end = int(tag[1]) -1
            entity_id = tag[2]
            html_tag_start = '<mark style="background-color: yellow'+';" title="'+entity_id+'">'
            html_tag_end = '</mark>'
        list_doc[start] = html_tag_start + list_doc[start]
        list_doc[end] = list_doc[end] + html_tag_end   
    total_results = ''.join(list_doc)
    return total_results

def submit(doc):
    """
    Callback function for when submit button is clicked.

    :param doc: clinical free text the user has entered
    :return: None
    """
    
    # set paramaters for the phenotagger model
    para_set={
            #model_type':para_model, # cnn or bioformer
            'onlyLongest': not para_overlap, # False: return overlap concepts, True: only longest
            'abbrRecog':para_abbr,# False: don't identify abbr, True: identify abbr
            'ML_Threshold':para_threshold,# the threshold of deep learning model
            }
    
    # get annotations from phenotagger
    st.session_state.tag_result_phenotagger =bioTag(doc,biotag_dic,nn_model,
                                                    onlyLongest=para_set['onlyLongest'], 
                                                    abbrRecog=para_set['abbrRecog'],
                                                    Threshold=para_set['ML_Threshold'])
    # get annotations from phenobert
    st.session_state.tag_result_phenobert_text, st.session_state.tag_result_phenobert = annotate_text(doc, use_longest=overlap_phenobert)

    if not st.session_state.tag_result_phenotagger and not st.session_state.tag_result_phenotagger:
        st.write('No Phenotypes Were Identified. Try Again.')
        st.stop()

    # remove tagged phenotypes below user specifed confidence score
    for tagged in st.session_state.tag_result_phenobert:
        if tagged[2] < pheno_threshold:
            st.session_state.tag_result_phenobert.remove(tagged)

    # append to tag to differentiate between the models
    for tag in st.session_state.tag_result_phenobert:
        tag.append('orange')
    for tag in st.session_state.tag_result_phenotagger:
        tag.append('yellow')

    st.session_state.total_results = highlight(doc)

    st.session_state.data_entity_phenobert, st.session_state.data_entity_phenotagger = data_entity(st.session_state.tag_result_phenobert, st.session_state.tag_result_phenotagger)

st.title("Clinical Free Text to HPO Code")

with st.expander("ℹ️ - About this app", expanded=True):

    st.write(
        """     
-   This is a web app based on Phenotagger\'s Streamlit Demo (Phenotagger is a dictionary and deep learning-based model): https://huggingface.co/spaces/lingbionlp/PhenoTaggger-Demo
-   The following features have been added:
    -   comparison of annotation results with the current SOTA model PhenoBERT (https://github.com/EclipseCN/PhenoBERT)
    -   user selection from the identified HPO codes
    -   a search bar for users to enter phenotypes that the models may have missed which uses the Human Phenotype Ontology API (https://hpo.jax.org/app/)

	    """
    )

    st.markdown("")

st.markdown("")
st.markdown("## 📌 Paste document ")

ce, c1, ce, c2, c3 = st.columns([0.07, 1, 0.07, 4, 0.07])
with c1:

    st.markdown("""
    <style>
    .big-font {
        font-size:18px !important;
    }
    .small-font {
        font-size:9px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("")

    st.markdown('<p class="big-font"><strong>PhenoBERT Options<strong></p>', unsafe_allow_html=True)

    #user define paramaters for phenobert
    overlap_phenobert = st.checkbox(
        "Overlap concept",
        value=True,
        help="Tick this box to identify overlapping concepts",
        key = 'overlap_phenobert',
    )
    pheno_threshold = st.slider(
        "Threshold",
        min_value=0.5,
        max_value=1.0,
        value=0.95,
        step=0.05,
        help="Pick the confidence score of the model for each identified phenotype.",
        key = 'pheno_threshold',
    )  

    st.markdown("")

    st.markdown('<p class="big-font"><strong>Phenotagger Options<strong></p>', unsafe_allow_html=True)

    # user define parameters for phenotagger 
    ModelType = st.radio(
        "Choose Phenotagger model",
        ["Bioformer(Default)", "CNN"],
        help="Bioformer is more precise, CNN is more efficient",
    )

    if ModelType == "Bioformer(Default)":
        # kw_model = KeyBERT(model=roberta)

        @st.cache(allow_output_mutation=True)
        
        # load phenotagger Bioformer model
        def load_model():

            ontfiles={'dic_file':'huggingface_phenotagger/dict_new/noabb_lemma.dic',
                'word_hpo_file':'huggingface_phenotagger/dict_new/word_id_map.json',
                'hpo_word_file':'huggingface_phenotagger/dict_new/id_word_map.json'}
    

            vocabfiles={'labelfile':'huggingface_phenotagger/dict_new/lable.vocab',
                        'config_path':'huggingface_phenotagger/vocab/bioformer-cased-v1.0/bert_config.json',
                        'checkpoint_path':'huggingface_phenotagger/vocab/bioformer-cased-v1.0/bioformer-cased-v1.0-model.ckpt-2000000',
                        'vocab_path':'huggingface_phenotagger/vocab/bioformer-cased-v1.0/vocab.txt'}
            modelfile='huggingface_phenotagger/vocab/bioformer_p5n5_b64_1e-5_95_hponew3.h5'
    

            biotag_dic=dic_ont(ontfiles)    

            nn_model=bioTag_Bioformer(vocabfiles)
            nn_model.load_model(modelfile)
            return nn_model,biotag_dic

        nn_model,biotag_dic = load_model()

    else:
        @st.cache(allow_output_mutation=True)

        # load phenotagger CNN model
        def load_model():
            ontfiles={'dic_file':'huggingface_phenotagger/dict_new/noabb_lemma.dic',
                'word_hpo_file':'huggingface_phenotagger/dict_new/word_id_map.json',
                'hpo_word_file':'huggingface_phenotagger/dict_new/id_word_map.json'}
    

            vocabfiles={'w2vfile':'huggingface_phenotagger/vocab/bio_embedding_intrinsic.d200',   
                        'charfile':'huggingface_phenotagger/vocab/char.vocab',
                        'labelfile':'huggingface_phenotagger/dict_new/lable.vocab',
                        'posfile':'huggingface_phenotagger/vocab/pos.vocab'}
            modelfile='./vocab/cnn_p5n5_b128_95_hponew1.h5'
    
            biotag_dic=dic_ont(ontfiles)    
        
            nn_model=bioTag_CNN(vocabfiles)
            nn_model.load_model(modelfile)
        
            return nn_model,biotag_dic

        nn_model,biotag_dic = load_model()
    para_overlap = st.checkbox(
        "Overlap concept",
        value=False,
        help="Tick this box to identify overlapping concepts",
        key = 'para_overlap',
    )
    para_abbr = st.checkbox(
        "Abbreviaitons",
        value=True,
        help="Tick this box to identify abbreviations",
        key = 'para_abbr',
    )        
    para_threshold = st.slider(
        "Threshold",
        min_value=0.5,
        max_value=1.0,
        value=0.95,
        step=0.05,
        help="Pick the confidence score of the model for each identified phenotype.",
        key = 'para_threshold',
    ) 

with c2:
       
    doc = st.text_area(
            "Paste your text below",
            value = 'The clinical features of Angelman syndrome (AS) comprise severe mental retardation, postnatal microcephaly, macrostomia and prognathia, absence of speech, ataxia, and a happy disposition. We report on seven patients who lack most of these features, but presented with obesity, muscular hypotonia and mild mental retardation. Based on the latter findings, the patients were initially suspected of having Prader-Willi syndrome. DNA methylation analysis of SNRPN and D15S63, however, revealed an AS pattern, ie the maternal band was faint or absent. Cytogenetic studies and microsatellite analysis demonstrated apparently normal chromosomes 15 of biparental inheritance. We conclude that these patients have an imprinting defect and a previously unrecognised form of AS. The mild phenotype may be explained by an incomplete imprinting defect or by cellular mosaicism.',
            height=525,
    )

    submit_button = st.button(label="✨ Submit!", on_click=clear)

if not submit_button and not st.session_state.button :
    st.stop()
else:
    st.session_state.button = True

st.markdown("")
st.markdown("## 💡 Tagged results:")

if submit_button:
    with st.spinner('Wait for tagging...'):
        submit(doc)

st.markdown('<font style="color: rgb(128, 128, 128);">Move the mouse🖱️ over the entity to display the HPO id. Phenotagger results are<mark style="background-color: yellow"> highlighted.</mark> PhenoBERT results are <u style="text-decoration: orange dashed underline 3px">underlined.</u></font>', unsafe_allow_html=True)

st.markdown('<table border="1"><tr><td>'+st.session_state.total_results+'</td></tr></table>', unsafe_allow_html=True)

st.markdown("")
st.markdown("")

df_phenotagger = data_upload(st.session_state.data_entity_phenotagger)
df_phenobert = data_upload(st.session_state.data_entity_phenobert)

df_combined = concat([df_phenotagger, df_phenobert])
df_combined_dup = df_combined.drop_duplicates(subset=['HPO ID'], keep='last')

c1, c2, c3 = st.columns([1, 4, 1])

with c2:
    st.markdown('<mark class="big-font"><strong>Results<strong></mark>', unsafe_allow_html=True)
    totalRows = df_combined_dup.shape[0]
    pre_rows_list = list(range(0,totalRows+1))
    grid_table_1 = generate_aggrid(df_combined_dup, pre_row=pre_rows_list, key='results')


st.header(':mag_right: Selection')
st.write("")

c2, c3, c4 = st.columns([3, 1, 3])

with c2:
    # allow user to enter own identified phenotypes into a search bar
    grid_table = []
    st.markdown('<p class="big-font"><strong>Phenotype Search<strong></p>', unsafe_allow_html=True)

    results_shown = st.radio(
        "Choose Max No. Shown Results",
        ['Three (3)', 'Eight (8)', 'All'],
        help="Choose number of results to be shown for each phenotype. Changing this value number will reset the selected phenotypes.",
        horizontal=True,
        on_change=res_max_change
        )

    additional_phenotypes = st.text_input('Phenotype Search', label_visibility='collapsed', value='Enter phenotypes separated by commas')
    pre_rows = []
    terms = additional_phenotypes.split(",")
    res_pd = []
    # if user changes max number results shown by the search bar
    if st.session_state.changed == True:
        st.session_state.df = DataFrame(columns=["HPO ID", "Given Term", "Official Term"]).reset_index(drop=True)
        st.session_state.known = []
    if additional_phenotypes != 'Enter phenotypes separated by commas':
        for term in terms:
            res_pd += api_call(term, results_shown)
    
    st.session_state.df = data_upload(res_pd)

    st.session_state.changed = False

    if not st.session_state.df.equals(st.session_state.prev_df):
        st.session_state.rerun +=1
    st.session_state.prev_df = st.session_state.df
    
    # allow selected phenotypes to exist between search reruns
    if len(st.session_state.prev_selec) > 0:
        for i in range(len(st.session_state.prev_selec)):
            if st.session_state.df['Given Term'].str.contains(st.session_state.prev_selec[i]['Given Term']).any():
                pre_rows += [st.session_state.prev_selec[i]['rowIndex']]
        grid_table = generate_aggrid(st.session_state.df, pre_row=pre_rows, key=str(st.session_state.rerun))
    else:
        grid_table = generate_aggrid(st.session_state.df, key=str(st.session_state.rerun))
    if str(st.session_state.rerun-1) in st.session_state:
        del st.session_state[str(st.session_state.rerun-1)]
    if not grid_table:
        grid_table = generate_aggrid(st.session_state.df, key=str(st.session_state.rerun))

st.session_state.prev_selec = grid_table['selected_rows']

# create/append to final selection dataframe that user can download
st.session_state.sel_rows = grid_table_1['selected_rows'] + grid_table['selected_rows'] 

df_sel_rows = data_upload(st.session_state.sel_rows)
    
with c4:
    st.markdown('<p class="big-font"><strong>Final Selection to Export <strong></p>', unsafe_allow_html=True)
    if not df_sel_rows.empty:
        final_grid_table = generate_aggrid_final(df_sel_rows, cellRend_1, cellRend_2, cellRend_3)

final_df = DataFrame(final_grid_table['selected_rows'])

# convert final selection to relevant file types
annotations_csv = convert_df_to_csv(final_df)
annotations_json = convert_df_to_json(final_df)
annotations_txt = convert_df_to_string(final_df)

c1, c2, c3 = st.columns([1, 1, 1])

with c2:
    st.download_button('Download HPO Annotations as CSV', data = annotations_csv, file_name='hpo_annotations.csv', mime='text/csv') 
    st.download_button('Download HPO Annotations as TXT', data = annotations_txt, file_name='hpo_annotations.txt') 
    st.download_button('Download HPO Annotations as JSON', data = annotations_json, file_name='hpo_annotations.json', mime='application/json')



    

# Clinical Free Text to HPO Code

This is a web app based on Phenotagger\'s Streamlit Demo (Phenotagger is a dictionary and deep learning-based model): https://huggingface.co/spaces/lingbionlp/PhenoTaggger-Demo.

The following features have been added:
- comparison of annotation results with the current SOTA model Phenobert (https://github.com/EclipseCN/PhenoBERT)
- user selection from the identified HPO codes
- a search bar for users to enter phenotypes that the models may have missed which uses the Human Phenotype Ontology API (https://hpo.jax.org/app/)


## How to run on local machine

The web app was developed with Python 3.7.16. You can run and edit this web app on your local machine using the following steps:

1. Download the Github project files
2. Download the following models' large files (download link: [models' files](https://drive.google.com/drive/folders/11YOvh_INpplIlRWGvL9_3DNlR_WGOmJA?usp=share_link)) :
    - huggingface_phenotagger files:
        - vocab/
    - PHENOBERT files:
        - embeddings/ 
        - models/ 

3. Organize the downloaded files so the file structure looks like:
```shell
- huggingface_phenotagger/
    -- vocab/
    -- dict_new/
    -- src/
- PHENOBERT/
    -- phenobert/
        --embeddings/
        --models/
        --data/
        --img/
        --utils/
    -- setup.py
- app_hpo.py/
- README.md/
- requirements/
```
2. Install dependencies:
```shell
pip install -r requirements.txt
python PHENOBERT/setup.py
```
3. Run the web app on localhost:
```shell
streamlit run app_hpo.py
```

## Citations:

- Y. Feng, L. Qi and W. Tian, "PhenoBERT: a combined deep learning method for automated recognition of human phenotype ontology," in IEEE/ACM Transactions on Computational Biology and Bioinformatics, doi: 10.1109/TCBB.2022.3170301.

- Ling Luo, Shankai Yan, Po-Ting Lai, Daniel Veltri, Andrew Oler, Sandhya Xirasagar, Rajarshi Ghosh, Morgan Similuk, Peter N Robinson, Zhiyong Lu. PhenoTagger: A Hybrid Method for Phenotype Concept Recognition using Human Phenotype Ontology. Bioinformatics, Volume 37, Issue 13, 1 July 2021, Pages 1884–1890.
[View in HTML](https://wcrp-cmip.github.io/CMIP7-CVs/experiment/experiment)

<section id="description">

# Experiment  (cmip7)

## Description
The experiments CV defines the set of standardized climate model experiments, specifying what each experiment is intended to explore—such as historical trends, future scenarios, or idealized conditions—so that results from different models can be meaningfully compared and combined.

</section>

<section id="info">

| Item | Reference |
| --- | --- |
| Type | `cmip7:experiment` |
| Pydantic class | [`experiment`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/experiment.py): Experiment |
| | |
| JSON-LD | `cmip7:experiment` |
| Expanded reference link | [https://wcrp-cmip.github.io/CMIP7-CVs/experiment](https://wcrp-cmip.github.io/CMIP7-CVs/experiment) |
| Developer Repo | [![Open in GitHub](https://img.shields.io/badge/Open-GitHub-blue?logo=github&style=flat-square)](https://github.com/wcrp-cmip/CMIP7-CVs//tree/main/src-data/experiment) |

</section>
<section id="links">

## 🔗 Links and Dependencies


## External Dependencies
**experiment** depends on **2 external vocabularies**  
**Path:** `universal:activity → universal:source-type`

The following external vocabularies are required to fully describe the data:


- `activity` → universal:activity [link](https://wcrp-cmip.github.io/WCRP-universe/activity/)
- `source-type` → universal:source-type [link](https://wcrp-cmip.github.io/WCRP-universe/source-type/)


### Contexts of External Mappings

- **`activity`** → `@type: @id`
  - Context: [https://wcrp-cmip.github.io/WCRP-universe/activity/\_context\_](https://wcrp-cmip.github.io/WCRP-universe/activity/_context_)
  - Source: `WCRP-universe/activity/_context_`

- **`model-realms`** → `@type: @id`
  - Context: [https://wcrp-cmip.github.io/WCRP-universe/source-type/\_context\_](https://wcrp-cmip.github.io/WCRP-universe/source-type/_context_)
  - Source: `WCRP-universe/source-type/_context_`

- **`parent-activity`** → `@type: @id`
  - Context: [https://wcrp-cmip.github.io/WCRP-universe/activity/\_context\_](https://wcrp-cmip.github.io/WCRP-universe/activity/_context_)
  - Source: `WCRP-universe/activity/_context_`


</section>

<section id="schema">

## Content Schema

- **`id`** (**str**) 
  << No description in pydantic model (see esgvoc) >>
- **`description`** (**str**) 
  << No description in pydantic model (see esgvoc) >>
- **`activity`** (**list**) 
  << No description in pydantic model (see esgvoc) >>
- **`additional_allowed_model_components`** (**list**) 
  << No description in pydantic model (see esgvoc) >>
- **`drs_name`** (**str**) 
  << No description in pydantic model (see esgvoc) >>
- **`end_year`** (**int | None**) 
  << No description in pydantic model (see esgvoc) >>
- **`experiment`** (**str**) 
  << No description in pydantic model (see esgvoc) >>
- **`experiment_id`** (**str**) 
  << No description in pydantic model (see esgvoc) >>
- **`min_number_yrs_per_sim`** (**int | None**) 
  << No description in pydantic model (see esgvoc) >>
- **`parent_activity_id`** (**list[str] | None**) 
  << No description in pydantic model (see esgvoc) >>
- **`parent_experiment_id`** (**list[str] | None**) 
  << No description in pydantic model (see esgvoc) >>
- **`required_model_components`** (**list[str] | None**) 
  << No description in pydantic model (see esgvoc) >>
- **`start_year`** (**int | None**) 
  << No description in pydantic model (see esgvoc) >>
- **`sub_experiment_id`** (**list[str] | None**) 
  << No description in pydantic model (see esgvoc) >>
- **`tier`** (**int | None**) 
  << No description in pydantic model (see esgvoc) >>
- **`type`** (**str**) 
  << No description in pydantic model (see esgvoc) >>


</section>   

<section id="usage">

## Usage

### Online Viewer 
#### Direct
To view a file in a browser use the content link with `.json` appended.

For example: `https://github.com/wcrp-cmip/CMIP7-CVs//tree/main/src-data/experiment/1pctco2-bgc.json`

#### Use cmipld.js [in development]
[View self resolving files here](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=cmip7%253Aexperiment/1pctco2-bgc)

### Getting a File

A short example of how to integrate the computed ld file into your code. 

```python
import cmipld
cmipld.get("cmip7:experiment/1pctco2-bgc")
```

### Framing
Framing is a way we can filter the downloaded data to match what we want. 
```python
frame = {
    "@context": "https://wcrp-cmip.github.io/CMIP7-CVs/experiment/_context_",
    "@type": "cmip7:experiment",
    "keys we want": "",
    "@explicit": True
}
        
import cmipld
cmipld.frame("cmip7:experiment/1pctco2-bgc", frame)
```
</section>

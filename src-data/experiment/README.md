[View in HTML](https://wcrp-cmip.github.io/CMIP7-CVs/experiment/experiment)

<section id="description">

# Experiment  (universal)

## Description


</section>

<section id="info">

| Item | Reference |
| --- | --- |
| Type | `wrcp:experiment` |
| Pydantic class | [`experiment`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/experiment.py): Experiment |
| | |
| JSON-LD | `cmip7:experiment` |
| Expanded reference link | [https://wcrp-cmip.github.io/CMIP7-CVs/experiment](https://wcrp-cmip.github.io/CMIP7-CVs/experiment) |
| Developer Repo | [![Open in GitHub](https://img.shields.io/badge/Open-GitHub-blue?logo=github&style=flat-square)](https://github.com/wcrp-cmip/CMIP7-CVs//tree/main/src-data/experiment) |

</section>
<section id="links">

## 🔗 External Links and Dependencies


### Context-based External Mappings

*Based on @context analysis*

- **`activity`** → `@type: @id`
  - Context: [https://wcrp-cmip.github.io/WCRP-universe/activity/\_context\_](https://wcrp-cmip.github.io/WCRP-universe/activity/_context_)
  - Source: `WCRP-universe/activity/_context_`

- **`model-realms`** → `@type: @id`
  - Context: [https://wcrp-cmip.github.io/WCRP-universe/source-type/\_context\_](https://wcrp-cmip.github.io/WCRP-universe/source-type/_context_)
  - Source: `WCRP-universe/source-type/_context_`

- **`parent-activity`** → `@type: @id`
  - Context: [https://wcrp-cmip.github.io/WCRP-universe/activity/\_context\_](https://wcrp-cmip.github.io/WCRP-universe/activity/_context_)
  - Source: `WCRP-universe/activity/_context_`


### Repository Breakdown

- **Organisation:** `WCRP-universe`
  - **Repository:** `activity`

- **Organisation:** `WCRP-universe`
  - **Repository:** `source-type`


</section>

<section id="depends">

## External Dependencies

### 🧭 Dependency Navigation
**experiment** depends on **2 external vocabularies**  
**Path:** `universal:activity → universal:source-type`


### Detailed Dependencies
The following external vocabularies are required to fully describe the data:

- [**universal**](https://wcrp-cmip.github.io/WCRP-universe/): [activity](https://wcrp-cmip.github.io/WCRP-universe/activity/)
- [**universal**](https://wcrp-cmip.github.io/WCRP-universe/): [source-type](https://wcrp-cmip.github.io/WCRP-universe/source-type/)

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
To view a file in a browser use the content link with `.json` appended. 
eg. https://github.com/wcrp-cmip/CMIP7-CVs//tree/main/src-data/experiment/1pctco2-bgc.json

### Getting a File

A short example of how to integrate the computed ld file into your code. 

```python
import cmipld
cmipld.get( "cmip7:experiment/1pctco2-bgc")
```

### Framing
Framing is a way we can filter the downloaded data to match what we want. 
```python
frame = {
            "@context": "https://wcrp-cmip.github.io/CMIP7-CVs/experiment/_context_",
            "@type": "wcrp:experiment",
            "keys we want": "",
            "@explicit": True
        }
        
import cmipld
cmipld.frame( "cmip7:experiment/1pctco2-bgc" , frame)
```
</section>

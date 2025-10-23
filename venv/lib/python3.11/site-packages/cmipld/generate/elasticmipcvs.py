
from cmipld import Frame
from cmipld.graph import JSONLDGraphProcessor
import asyncio

from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv
# load_dotenv()

home_dir = os.path.expanduser('~')
env_path = os.path.join(home_dir, '.env')
# Load environment variables from the .env file
load_dotenv(dotenv_path=env_path)


async def main():
    files = ['cmip6plus_ld', 'mip_cmor_tabes_ld']

    # Initialize the Elasticsearch client with correct parameters
    es = Elasticsearch(
        ['https://127.0.0.1:9200'],
        basic_auth=('elastic', os.environ['ELASTIC_PASSWORD']),
        verify_certs=True,  # Enable certificate verification
        ca_certs=os.environ['ELASTIC_CERTS']  # Path to CA certificate
    )

    # https://www.elastic.co/guide/en/elasticsearch/reference/current/targz.html

    # # Process input files
    # ldcontent = await CMIPFileUtils().load(files)
    # print("Graph processing completed.")
    graph = JSONLDGraphProcessor()

    await graph.make_graph(files)

    print("Graph processing completed.")
    ldcontent = graph.lddata
    core_frame = graph.generate_frames
    linked_frame = graph.link_frames

    indexes = []
    errors = []

    for fname, fvalue in linked_frame.items():
        print("Linked Frame: ", fname)
        # print('--',fvalue)
        if '@context' in fvalue:
            del fvalue['@context']

        data = Frame(ldcontent, fvalue).clean(['untag', 'rmnoparent']).data

        index, doc = fname.split(':')
        indexes.append(index)

        # add to
        counter = 0

        for entry in data:
            print('\n\n', entry["@id"], '\n', entry)
            try:
                es.index(index=index, id=entry["@id"], body=entry)
                counter += 1
            except Exception as e:
                print(e)
                print('Error in adding document to index')
                errors.append([entry['@id'], entry, e])

        print(f'Added {counter} documents to index')

    for index in indexes:
        es.indices.refresh(index=index)
        print(f'Index {index} has been refreshed')

    # for i in errors:
    #     for j in i:
    #         print(j)
    #     print('\n\n')

    for i in errors:
        print(f'\n\n{i[0]}\n - {i[-1]}')


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()

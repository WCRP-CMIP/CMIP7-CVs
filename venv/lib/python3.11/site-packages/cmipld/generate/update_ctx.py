from ..locations import mapping
from ..utils import sorted_ctx
from collections import OrderedDict

import glob
import json
import tqdm
import os

from ..locations import reverse_mapping
reverse = reverse_mapping

repo = os.popen("git remote get-url origin").read().replace('.git',
                                                            '').strip('\n').split('/')[-2:]
base = f'https://{repo[0].lower()}.github.io/{repo[1]}/'
# sort by length of key
mapping = dict(sorted(mapping.items(), key=lambda item: len(item[0])))
mapping['id'] = '@id'
mapping['type'] = '@type'
mapping['entries'] = '@none'

historic = ['id', 'type']





def main():

    # note, an easier, but messier way can achieved by speifying two contexts in the file.
    # @context: [context1, context2]

    ctxs = glob.glob('src-data/*/*_context_')
    print('Updating contexts: to match latest repository prefixes')
    for cx in tqdm.tqdm(ctxs):
        # print(cx)

        item = cx.split('/')[1]

        try:
            try:
                data = json.load(open(cx))
            except:
                data = {'@context': {'id': '@id', 'type': '@type', 'entries': '@none'}}

            ctx = data['@context']

            # we can ignore one line ctx
            if isinstance(ctx, list):
                if len(ctx) > 1:
                    ctx = ctx[1]
                    # we can ignore one line ctx
                else:
                    ctx = {}

            # this will be removed eventually
            for rm in historic:
                if rm in ctx:
                    # list comprehension to remove historic prefixes from mapping
                    del ctx[rm]

            ctx = OrderedDict(sorted((k, v) for k, v in ctx.items()))

            # ensure the base and vocab are correct
            ctx['@base'] = f"{base}{item}/"
            ctx['@vocab'] = ctx['@base']
            # lets glue together with the global context
            ctx = [f"../_context_", ctx]
            # update the ctx
            data['@context'] = ctx
            data = sorted_ctx(data)

            data['@type'] = [reverse[base]]

            with open(cx, 'w') as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            print(f"Error: {str(e)}")
            print(f"Error with {cx}")
            continue

    # lets write the root repo
    with open('./src-data/_context_', 'w') as f:
        data = {"@context": mapping}

        data['@context']['@base'] = base
        data['@context']['@vocab'] = base

        data = sorted_ctx(data)

        json.dump(data, f, indent=4)

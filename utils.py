
from engine.cranfield import CranfieldGetter, dataset as cranfield_dataset
from engine.core import IRS
from itertools import islice


def populateIrs(irs: IRS, datasetSlug: str = 'cranfield', maxDocs: int = 2000):
  if datasetSlug == 'cranfield':
    irs.data_getter = CranfieldGetter()
    irs.add_documents((d.doc_id for d in islice(cranfield_dataset.docs_iter(), maxDocs)))
  else:
    raise ValueError(f"Unknown dataset {datasetSlug}")
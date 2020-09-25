import glob
from igraph import Graph
import pandas as pd
import pickle

stringRawPath = "/media/data/NetworkDB/STRING_raw/9606.protein.links.detailed.v11.0.txt"
stringdf = pd.read_csv(stringRawPath, sep = " ",)


stringdf["neighborhood"] = stringdf["neighborhood"]/1000
stringdf["fusion"] = stringdf["fusion"]/1000
stringdf["cooccurence"] = stringdf["cooccurence"]/1000
stringdf["coexpression"] = stringdf["coexpression"]/1000
stringdf["experimental"] = stringdf["experimental"]/1000
stringdf["database"] = stringdf["database"]/1000
stringdf["textmining"] = stringdf["textmining"]/1000
stringdf["combined_score"] = stringdf["combined_score"]/1000

stringdf_filter = stringdf[stringdf["combined_score"] >= 0.7]
stringdf_filter["protein_str"] = stringdf_filter[['protein1', 'protein2']].apply(lambda x: '_'.join(sorted(x)), axis=1)
stringdf_filter.drop_duplicates('protein_str', inplace=True)
stringdf_filter["protein1"] = stringdf_filter['protein1'].apply(lambda x: x.split(".")[1])
stringdf_filter["protein2"] = stringdf_filter['protein2'].apply(lambda x: x.split(".")[1])

aa = pd.concat([stringdf_filter["protein1"], stringdf_filter["protein2"]]).unique().tolist()
stringGraph = Graph()
stringGraph.add_vertices(aa)


#load annotations
annots = pd.read_csv("/media/data/NetworkDB/STRING_raw/9606.protein.info.v11.0.txt", sep="\t")
annots.head()

annots["protein_external_id"] = annots["protein_external_id"].apply(lambda x: x.split(".")[1])
annots.set_index("protein_external_id", drop=True, inplace=True, verify_integrity=True)


for elem in stringGraph.vs:
    elem["gene_name"] = annots.loc[stringGraph.vs["name"], "preferred_name"]
    elem["protein_size"] = annots.loc[stringGraph.vs["name"], "protein_size"]
    elem["annotation"] = annots.loc[stringGraph.vs["name"], "annotation"]
input("proceed with pickling graph?")
pickle.dump(stringGraph,open("/media/data/NetworkDB/STRING_raw/STRING_Combined07_NEW.graph", "wb"))

print("done")

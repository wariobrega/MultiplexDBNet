# create an igraph network (stored in a pickle object) that stores validate miRNA-Gene interactions

import sys
import pickle
import pandas as pd
from igraph import Graph


mirtarbasepath = "/mnt/c/Users/IEO5144/OneDrive - Istituto Europeo di Oncologia/Programming/MultiplexDBNet/raw_data/MirTarBase/hsa_MTI.xlsx"

# def parseMirTarBase(mirtarbasepath=mirtarbasepath):
#     """
#     parse the excel file containing mirtarbase interactions (we work here ONLY on HS-HS miRNA)
#     """
#     # create a dictionary of values storing an arbitrary strenght of the interactions 
#     functionalstrengthdic = {"Strong": 3, "Weak": 1} #3 weak interactions are required to compensate for a single "Strong" functional MTI
#     print("Reading MirtarBase original file...")
#     mirtarbasehsdf = pd.read_excel(mirtarbasepath, names=["miRTarBase_ID", "miRNA", "miRNA_Species", "Target_Gene", "ENTREZID", "Target_Gene_Species", "Experiments", "Support", "PMID"])
#     # print(mirtarbasehsdf.head())
#     # print(mirtarbasehsdf.shape)
#     # print(mirtarbasehsdf.Support.unique())
#     #remove-non functional MTI interaction
#     print("Removing non functional MTI...")
#     mirtarbasehsdf = mirtarbasehsdf[~mirtarbasehsdf.Support.isin(["Non-Functional MTI", "Non-Functional MTI (Weak)"])]
#     # print(mirtarbasehsdf.head())
#     # replace functional mti with more comfy names and map a numeric score to each MTI 
#     print("Replacing Functional Keyword with more comy ones...")
#     mirtarbasehsdf.Support.replace("Functional MTI (Weak)", "Weak", inplace=True)
#     mirtarbasehsdf.Support.replace("Functional MTI", "Strong", inplace=True)
#     # print(mirtarbasehsdf.head())
#     # print(mirtarbasehsdf.Support.unique())
#     print ("Adding numeric score to each support evidence")
#     # mirtarbasehsdf["Support_num"] = mirtarbasehsdf.apply(lambda row: functionalstrengthdic[row.Support], axis = 1)
#     mirtarbasehsdf["Support_num"] = mirtarbasehsdf.Support.map(functionalstrengthdic) #map seems way faster than the apply + lambda
#     #finally, add a mir-mrna colum for retrieveing the miRNA mRNA interaction
#     print("Adding a final column summarizing interactions for later on...")
#     mirtarbasehsdf["MTI"] = mirtarbasehsdf.miRNA + "__" + mirtarbasehsdf.Target_Gene
#     print(mirtarbasehsdf.head())
#     return mirtarbasehsdf

# def createMirTarBaseNetwork(mirtarbasedf = parseMirTarBase()):
#     """
#     create the network of MirtarBase miRNA-miRNA interactions
#     """
#     mirTarBaseGraph = Graph()
#     print(mirTarBaseGraph.summary())
#     print("Adding nodes...")
#     mirnas = mirtarbasedf.miRNA.unique().tolist()
#     genes = mirtarbasedf.Target_Gene.unique().tolist()
#     print("number of miRNAs:", len(mirnas), sep = "\t") 
#     print("number of genes:", len(genes), sep = "\t")
#     allnodes = mirnas + genes
#     mirTarBaseGraph.add_vertices(allnodes)
#     print(mirTarBaseGraph.summary())
#     print("Adding node attributes...")
#     for elem in mirnas:
#         ind = mirTarBaseGraph.vs.find(name = elem).index
#         mirTarBaseGraph.vs[ind]["type"] = "miRNA"
    
#     for elem in genes:
#         ind = mirTarBaseGraph.vs.find(name = elem).index
#         mirTarBaseGraph.vs[ind]["type"] = "Gene"
#         mirTarBaseGraph.vs[ind]["EntrezID"] = mirtarbasedf[mirtarbasedf.Target_Gene == elem]["ENTREZID"].iloc[0]
#     print(mirTarBaseGraph.summary())
#     print("Adding Edges...")
#     #save stuff temporarily (to work on edges...)
#     temp = [tuple(x) for x in pd.Series(mirtarbasedf.MTI.unique()).str.split("__").tolist()]
#     print("Adding edges...")
    
#     mirTarBaseGraph.add_edges(temp)
    
#     print("Adding edge attributes, this may take a while...")
    
#     grouped = mirtarbasedf.groupby("MTI")
#     support_sum = grouped.agg(Support_sum = pd.NamedAgg(column='Support_num', aggfunc='sum'))
#     support_sum["N_PMIDs"] = grouped.PMID.size()
    
#     #add the PMID dictionary 
#     for i, elem in grouped:
#         tmp = i.split("__")
#         # print(tmp)
#         # input()
#         source = mirTarBaseGraph.vs.find(name=tmp[0]).index
#         target = mirTarBaseGraph.vs.find(name=tmp[1]).index
#         sel = mirTarBaseGraph.es.select(_between=((source,), (target,)))
#         if len(sel) > 1:
#             raise ValueError("this should be 1")
        
#         sel["PMIDS_evidences"] = dict(zip(elem.PMID.tolist(), elem.Experiments.str.split("//"))) 
#         sel["PMIDs_support"] = dict(zip(elem.PMID.tolist(), elem.Support.tolist()))
#         sel["PMIDs_total"] = support_sum.loc[i, "N_PMIDs"]
#         sel["Support_score"]  = support_sum.loc[i, "Support_sum"]
    
#     return mirTarBaseGraph

# def saveMirtarbase(mirtarbasegraph=createMirTarBaseNetwork(), path = "/mnt/c/Users/IEO5144/OneDrive - Istituto Europeo di Oncologia/Programming/MultiplexDBNet/networks/MirTarBase/MirTarBase_HS_Main.graph"):
#     print("Saving to .graph file...")
#     mirtarbasegraph.write_pickle(path)
#     print("Done!")
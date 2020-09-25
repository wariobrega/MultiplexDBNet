#Convert the DoroThea Network to a network file
from igraph import Graph
import pandas as pd
import sys
import os
import pickle 

def importDorothea(dorotheapath):
    """
    Parse the dorothea Network and turn it into a pandas dataframe ready to be imported into a graph 
    """
    #dictionary that stores all the confidence intervals for Dorothea
    confidencedict = {"A": 5,
                 "B": 4,
                 "C": 3,
                 "D" : 2,
                 "E" : 1}
    print("Importing the datatset using Pandas...")
    dorotheadf = pd.read_csv(dorotheapath, sep = "\t")
    dorotheadf['confidence_num'] = dorotheadf.confidence.map(confidencedict)
    # adress the mutual tf -- > target interactions
    print("Number of starting entries (edges): ", dorotheadf.shape[0], sep = "\t")
    return dorotheadf

def dorotheadftoEdgesdf(dorotheadf):
    """
    reparse the dataframe stgoring dorothea to adress that pesky multiple loop problem
    """

    print("Parsing the dataframe to address the pesky mutual loops...")
    allpairs = []
    
    for i, elem in dorotheadf.iterrows():
        tf = elem.tf
        target = elem.target
        pair = "___".join(sorted([tf, target]))
        allpairs.append(pair)
    
    dorotheadf["pair"] = allpairs
    dorotheadf["mutual"] = dorotheadf["pair"].duplicated(keep=False) 

    grouped = dorotheadf.groupby("pair") #aggregate by the pair
    edge_vals = grouped.agg(mor_sum=pd.NamedAgg(column='mor', aggfunc='sum'),confidence_mean=pd.NamedAgg(column='confidence_num', aggfunc='mean'))
    grouped_confs = grouped["confidence"].agg(lambda column: list(column))
    grouped_mutual = grouped["mutual"].first()
    edge_vals["grouped_confs"] = grouped_confs
    edge_vals["mutual"] = grouped_mutual
    edge_vals["pair"] = edge_vals.index
    edge_vals["p1"] = [x.split("___")[0] for x in edge_vals.index.tolist()]
    edge_vals["p2"] = [x.split("___")[1] for x in edge_vals.index.tolist()]
    edge_vals.reset_index(drop=True, inplace=True)
    # print(edge_vals.head())
    print("Done! Returning Edge dataframe...")
    return edge_vals

def dorotheadfToGraph(nodesdf, edgesdf):
    """
    create the dorothea graph
    """
    #add edges from the original dorothea df
    print("Creating Dorothea Graph.")
    print("Creting vertices...")
    dorotheagraph = Graph()
    nodestfs = nodesdf.tf.unique().tolist()
    #miss: add disctinction between who is tf and who is a target
    nodestargets = nodesdf.target.unique().tolist()
    dorotheavs = list(set(nodestfs + nodestargets))
    dorotheagraph.add_vertices(dorotheavs)
    #define the type of each of the nodes
    for elem in dorotheagraph.vs:
        if elem["name"] in nodestfs:
            elem["type"] = "TF"
        else:
            elem["type"] = "Target"

    print("Summary after Vertex Adding:\n")
    print(dorotheagraph.summary())

    edgeslist = [list(x) for x in list(zip(edgesdf.p1.tolist(), edgesdf.p2.tolist()))]
    # aa = list(set(edgesdf.p1.unique().tolist() + edgesdf.p2.unique().tolist()))
    # print(len(aa))
    dorotheagraph.add_edges(edgeslist) #add all edges
    print("Summary after Edges Adding:\n")
    print(dorotheagraph.summary())

    #write temporary graph here
    dorotheagraph.write_pickle("/mnt/c/Users/IEO5144/OneDrive - Istituto Europeo di Oncologia/Programming/MultiplexDBNet/networks/Dorothea_MAIN.graph")

    print("Adding Edge Attributes, this may take a while...")
    for i,elem in edgesdf.iterrows():
        source = dorotheagraph.vs().find(name=elem.p1).index
        target = dorotheagraph.vs().find(name=elem.p2).index

        essel = dorotheagraph.es().select(_between=((source,), (target,)))
        if len(essel) != 1: #check on graph integrity
            raise ValueError("this should be 1")
        
        else:
            correctedge = essel[0]
            correctedge["mutual"] = elem.mutual
            correctedge["confidence_score"] = elem.grouped_confs
            correctedge["mor"] = elem.mor_sum
            correctedge["confidence_score_numeric"] = elem.confidence_mean 
    
    return dorotheagraph

dorothearaw = "/mnt/c/Users/IEO5144/OneDrive - Istituto Europeo di Oncologia/Programming/MultiplexDBNet/raw_data/DoRoThEA/Dorothea_HS_full.tsv"
nodesdf = importDorothea(dorothearaw)
edgesdf = dorotheadftoEdgesdf(nodesdf)

def saveDorothea(dorotheagraph = dorotheadfToGraph(nodesdf=nodesdf, edgesdf = edgesdf), path = "/mnt/c/Users/IEO5144/OneDrive - Istituto Europeo di Oncologia/Programming/MultiplexDBNet/networks/Dorothea_MAIN.graph")>
    print("Saving to .graph*pickle object..")
    dorotheagraph.write_pickle(path)
    print("Done!")
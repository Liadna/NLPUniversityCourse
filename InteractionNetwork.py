import os
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pylab
from nltk.sentiment import SentimentIntensityAnalyzer
import SentimentAnalysis


def read_files_to_dict(dir_path):
    """
    Read file in specified path
    :param file_path: Path of file to read
    :return: Conversations formatted in the file
    """
    conversations = {}
    for filename in os.listdir(dir_path):
        if filename.endswith(".txt"):
            file_path = os.path.abspath(os.path.join(dir_path, filename))
            with open(file_path, 'r') as f:
                x = f.readlines()
                content_unicode = unicode(x[0], encoding='utf-8', errors='replace')
                sentences = content_unicode.split('@')
                if not filename in conversations:
                    conversations[filename.split('.txt')[0]] = sentences
    return conversations


def build_sentiment_graph(nodes, edges):
    """
    Set nodes and edges to form a graph describing the sentiments in the conversations between characters.
    Uses the implementation of networkx python package for the graphs
    :param nodes: Nodes of the graph
    :param edges: Edges of the graph
    :return: Graph
    """
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node, name=node)
    for edge in edges:
        u = edges[edge]['from']
        v = edges[edge]['to']
        weight = edges[edge]['weight']
        color = edges[edge]['color']
        G.add_edge(u, v, weight=weight, color=color)

    return G


def create_nodes(conversations):
    """
    Set each unique character as a node in the graph
    :param conversations: Conversations of all the characters
    :return: Nodes as characters
    """
    characters = []
    for conv_name in conversations.keys():
        if '-' not in conv_name:
            characters.append(conv_name)
    characters.remove('BackGround')
    return characters


def create_edges(conversations):
    """
    Set each interaction between two characters as an edge.
    For each character saves the speacking characters and the second character, and colors the edge according to the sentiment score.
    :param conversations: Conversations of all the characters
    :return: Edges as characters
    """
    edges = {}
    characters = create_nodes(conversations)
    sid = SentimentIntensityAnalyzer()
    for character in characters:
        char_conversations = SentimentAnalysis.get_all_character_conversations(character=character, conversations=conversations)
        for name, conversation in char_conversations.iteritems():
            avg_score, label = SentimentAnalysis.classify_conversation(conversation, analyzer=sid)
            if '-' in name:
                first_character, second_character = name.split('-')
                if first_character in characters and second_character in characters:
                    edges[name] = {}
                    edges[name]['from'] = first_character
                    edges[name]['to'] = second_character
                    edges[name]['weight'] = format(avg_score, '.2f')
                    if label == 'Positive':
                        edges[name]['color'] = 'g'
                    elif label == 'Negative':
                        edges[name]['color'] = 'r'
                    else:
                        edges[name]['color'] = 'b'
    return edges


def draw_graph(G):
    """
    Draw the graph as an matplotlib image.
    The direction of the edge is used to indicate the overall sentiment of the sentences spoken by a character
     to another character.
        Green edges indicate positive sentiment,
        blue indicate neutral sentiment ,
        red indicate negative sentiment.
    The labels on the edges show the average score of the sentiment on all the sentences a character spoke during the conversation.
    The width of an edge is proportional to the length of the conversation, which is considered as the number of
     sentences that the character spoke, normalized to the total number of collected sentences.
    :param G: Given graph
    :return: None
    """
    plt.figure(figsize=(10, 8))

    # node_color = [node['color'] for node in G.nodes()]
    color = nx.get_edge_attributes(G, 'color')
    names = nx.get_node_attributes(G, 'name')
    edge_colors = [color[edge] for edge in G.edges()]
    edge_labels = dict([((u, v,), d['weight'])
                        for u, v, d in G.edges(data=True)])

    pos = nx.circular_layout(G, scale=2)
    # pos = nx.spring_layout(G)
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, font_size=8)
    nx.draw(G, pos=pos, node_color=range(len(G)), edge_color=edge_colors, node_size=1500, with_labels=True)
    # pylab.show()
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def main():
    dir_path = r"./Spongebob NLP"
    conversations = read_files_to_dict(dir_path)

    nodes = create_nodes(conversations)
    edges = create_edges(conversations)
    G = build_sentiment_graph(nodes, edges)
    draw_graph(G)


if __name__ == '__main__':
    main()

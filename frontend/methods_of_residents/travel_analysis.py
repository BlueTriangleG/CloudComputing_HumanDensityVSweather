import pandas as pd
import json
import re
import matplotlib.pyplot as plt
import seaborn as sns

# 定义出行方式关键字
travel_modes = {
    'car': ['car', 'automobile', 'vehicle'],
    'bus': ['bus', 'coach'],
    'bike': ['bike', 'bicycle', 'cycling'],
    'walk': ['walk', 'walking', 'foot'],
    'train': ['train', 'railway', 'subway'],
    'scooter': ['scooter', 'e-scooter']
}

def load_mastodon_data(file_path):
    with open(file_path, 'r') as f:
        mastodon_data = json.load(f)
    
    records = []
    for record in mastodon_data:
        source = record['_source']
        location = None
        for tag in source.get('tags', []):
            if tag.lower() in ['melbourne', 'sydney', 'brisbane']:  # 添加希望识别的地名
                location = tag.lower().capitalize()
                break
        if not location:
            location = 'Unknown'  # 如果未找到标签，则设置为 'Unknown'
        
        records.append({
            'post_id': source['id'],
            'created_at': source['created_at'],
            'tokens': source['tokens'],  # 使用 tokens 字段
            'tags': source['tags'],
            'location': location
        })
    
    mastodon_df = pd.DataFrame(records)
    mastodon_df['created_at'] = pd.to_datetime(mastodon_df['created_at'])
    
    if mastodon_df['created_at'].dt.tz is None:
        mastodon_df['created_at'] = mastodon_df['created_at'].dt.tz_localize('UTC')
    else:
        mastodon_df['created_at'].dt.tz_convert('UTC')
    
    return mastodon_df

def extract_travel_modes(tokens):
    modes = []
    for mode, keywords in travel_modes.items():
        for token in tokens:
            if token.lower() in keywords:
                modes.append(mode)
                break
    return modes

def analyze_travel_modes(mastodon_df):
    # 提取出行方式
    mastodon_df['travel_modes'] = mastodon_df['tokens'].apply(extract_travel_modes)
    mastodon_df = mastodon_df.explode('travel_modes')
    
    # 按地区和出行方式统计
    travel_stats = mastodon_df.groupby(['location', 'travel_modes']).size().reset_index(name='counts')
    
    # 找出每个地区最流行的出行方式
    most_popular_travel_modes = travel_stats.loc[travel_stats.groupby('location')['counts'].idxmax()]
    
    return travel_stats, most_popular_travel_modes

def visualize_travel_modes(travel_stats):
    plt.figure(figsize=(12, 8))
    sns.barplot(x='location', y='counts', hue='travel_modes', data=travel_stats)
    plt.title('Most Popular Travel Modes by Location', fontsize=16)
    plt.xlabel('Location', fontsize=14)
    plt.ylabel('Counts', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.legend(title='Travel Modes')
    plt.show()
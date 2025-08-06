#!/usr/bin/env python3
"""
采访稿解析程序
支持解析和合并多个JSON格式的采访记录，输出为Markdown格式
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any


def parse_transcript(file_path: str) -> List[Dict[str, Any]]:
    """
    解析单个JSON文件，提取采访内容
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        包含发言记录的列表，每条记录包含speaker_name, content, start_time
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    transcript = []
    
    # 提取采访内容
    if 'minutes' in data and 'paragraphs' in data['minutes']:
        paragraphs = data['minutes']['paragraphs']
        
        for paragraph in paragraphs:
            # 获取发言人信息
            speaker_name = paragraph.get('speaker', {}).get('user_name', '未知发言人')
            
            # 获取发言内容
            content_parts = []
            for sentence in paragraph.get('sentences', []):
                for word in sentence.get('words', []):
                    text = word.get('text', '')
                    if text:
                        content_parts.append(text)
            
            if content_parts:
                content = ''.join(content_parts)
                start_time = paragraph.get('start_time', 0)
                
                transcript.append({
                    'speaker_name': speaker_name,
                    'content': content,
                    'start_time': start_time
                })
    
    return transcript


def merge_transcripts(transcripts: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    合并多个采访记录，按时间排序
    
    Args:
        transcripts: 多个采访记录列表
        
    Returns:
        合并后的采访记录，按时间排序
    """
    merged = []
    for transcript in transcripts:
        merged.extend(transcript)
    
    # 按start_time排序
    merged.sort(key=lambda x: x['start_time'])
    
    return merged


def format_to_markdown(transcript: List[Dict[str, Any]]) -> str:
    """
    将采访记录格式化为Markdown
    
    Args:
        transcript: 采访记录列表
        
    Returns:
        Markdown格式的字符串
    """
    lines = []
    
    for record in transcript:
        speaker_name = record['speaker_name']
        content = record['content']
        
        # 按指定格式输出
        lines.append(f"**[{speaker_name}]**: {content}\n")
    
    return '\n'.join(lines)


def main():
    """主程序"""
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python parse_transcript.py <json文件1> [json文件2] ...")
        print("  例如：python parse_transcript.py data-1.json")
        print("  或：python parse_transcript.py data-1.json data-2.json")
        sys.exit(1)
    
    file_paths = sys.argv[1:]
    all_transcripts = []
    
    # 解析所有文件
    for file_path in file_paths:
        if not Path(file_path).exists():
            print(f"警告：文件 {file_path} 不存在，跳过")
            continue
        
        try:
            print(f"正在解析：{file_path}")
            transcript = parse_transcript(file_path)
            all_transcripts.append(transcript)
            print(f"  提取了 {len(transcript)} 条发言记录")
        except Exception as e:
            print(f"错误：解析 {file_path} 失败 - {e}")
            continue
    
    if not all_transcripts:
        print("错误：没有成功解析任何文件")
        sys.exit(1)
    
    # 合并所有记录
    if len(all_transcripts) > 1:
        print("\n正在合并多个文件的记录...")
        merged_transcript = merge_transcripts(all_transcripts)
    else:
        merged_transcript = all_transcripts[0]
    
    print(f"总共 {len(merged_transcript)} 条发言记录\n")
    
    # 格式化为Markdown
    markdown_output = format_to_markdown(merged_transcript)
    
    # 输出到标准输出
    print("=" * 50)
    print("采访稿（Markdown格式）")
    print("=" * 50)
    print(markdown_output)
    
    # 同时保存到文件
    output_file = "transcript.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_output)
    print(f"\n结果已保存到：{output_file}")


if __name__ == "__main__":
    main()
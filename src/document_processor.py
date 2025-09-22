"""
Document processing module for handling PDF and XBRL files
"""
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
from lxml import etree
import re
from config import Config

class DocumentProcessor:
    """Handles processing of financial documents (PDF and XBRL)"""
    
    def __init__(self):
        self.config = Config()
    
    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process a document and return structured text chunks
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of dictionaries containing text chunks with metadata
        """
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return self._process_pdf(file_path)
        elif file_extension in ['.xml', '.htm']:
            return self._process_xbrl(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Process PDF files and extract text chunks"""
        chunks = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        # Clean and chunk the text
                        cleaned_text = self._clean_text(text)
                        page_chunks = self._chunk_text(cleaned_text)
                        
                        for chunk_idx, chunk in enumerate(page_chunks):
                            chunks.append({
                                'text': chunk,
                                'source': file_path,
                                'page': page_num + 1,
                                'chunk_index': chunk_idx,
                                'document_type': 'pdf'
                            })
        
        except Exception as e:
            print(f"Error processing PDF {file_path}: {str(e)}")
            raise
        
        return chunks
    
    def _process_xbrl(self, file_path: str) -> List[Dict[str, Any]]:
        """Process XBRL files and extract structured data"""
        chunks = []
        
        try:
            # Parse XBRL facts
            facts_df = self._parse_xbrl_facts(file_path)
            
            # Group facts by category for better context
            grouped_facts = self._group_xbrl_facts(facts_df)
            
            for category, facts in grouped_facts.items():
                # Create readable text from facts
                text = self._format_xbrl_facts(category, facts)
                
                if text.strip():
                    # Chunk the formatted text
                    text_chunks = self._chunk_text(text)
                    
                    for chunk_idx, chunk in enumerate(text_chunks):
                        chunks.append({
                            'text': chunk,
                            'source': file_path,
                            'category': category,
                            'chunk_index': chunk_idx,
                            'document_type': 'xbrl',
                            'fact_count': len(facts)
                        })
        
        except Exception as e:
            print(f"Error processing XBRL {file_path}: {str(e)}")
            raise
        
        return chunks
    
    def _parse_xbrl_facts(self, file_path: str) -> pd.DataFrame:
        """Parse XBRL XML for all facts"""
        tree = etree.parse(file_path)
        ns = tree.getroot().nsmap
        
        records = []
        for fact in tree.iterfind('.//*'):
            tag = fact.tag
            qname = etree.QName(tag)
            
            if qname.namespace is None:
                continue
                
            # Exclude known non-fact tags
            if qname.localname.lower() in [
                "context", "unit", "identifier", "segment", "entity", 
                "period", "startdate", "enddate", "instant", "measure", 
                "divide", "unitnumerator", "unitdenominator", "schemaRef"
            ]:
                continue
                
            value = fact.text
            if value is None or value.strip() == '':
                continue
                
            context_ref = fact.attrib.get('contextRef', 'N/A')
            unit_ref = fact.attrib.get('unitRef', '')
            
            # Get prefix from namespace map
            prefix = None
            for k, v in ns.items():
                if v == qname.namespace:
                    prefix = k
                    break
            
            if prefix:
                name = f"{prefix}:{qname.localname}"
            else:
                name = qname.localname
                
            records.append({
                "name": name,
                "context_ref": context_ref,
                "unit_ref": unit_ref,
                "value": value.strip()
            })
        
        return pd.DataFrame(records)
    
    def _group_xbrl_facts(self, facts_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Group XBRL facts by category for better context"""
        grouped = {}
        
        # Group by prefix (us-gaap, dei, etc.)
        for prefix in facts_df['name'].str.split(':').str[0].unique():
            if pd.isna(prefix):
                continue
            prefix_facts = facts_df[facts_df['name'].str.startswith(f"{prefix}:")]
            if len(prefix_facts) > 0:
                grouped[prefix] = prefix_facts
        
        return grouped
    
    def _format_xbrl_facts(self, category: str, facts: pd.DataFrame) -> str:
        """Format XBRL facts into readable text"""
        text_parts = [f"Financial Data - {category.upper()} Category:"]
        
        # Group by fact name for better readability
        for fact_name, group in facts.groupby('name'):
            fact_name_clean = fact_name.split(':')[-1].replace('_', ' ').title()
            text_parts.append(f"\n{fact_name_clean}:")
            
            for _, fact in group.iterrows():
                value = fact['value']
                context = fact['context_ref']
                unit = fact['unit_ref']
                
                # Format the fact
                fact_text = f"  - Value: {value}"
                if unit:
                    fact_text += f" ({unit})"
                if context != 'N/A':
                    fact_text += f" [Context: {context}]"
                
                text_parts.append(fact_text)
        
        return '\n'.join(text_parts)
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
        return text.strip()
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks of specified size"""
        words = text.split()
        chunks = []
        
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > self.config.CHUNK_SIZE:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_length = len(word)
                else:
                    # Single word is longer than chunk size
                    chunks.append(word)
                    current_length = 0
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

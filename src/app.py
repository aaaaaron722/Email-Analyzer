from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from transformers import T5Tokenizer, T5ForConditionalGeneration, BartTokenizer, BartForConditionalGeneration
import torch
from pathlib import Path
from transformers.utils import logging as transformers_logging

# 設置日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
transformers_logging.set_verbosity_info()

app = Flask(__name__)
CORS(app)

class EmailGenerator:
    def __init__(self):
        logger.info("Loading the model...")
        try:
            cache_dir = Path("./model_cache")
            cache_dir.mkdir(exist_ok=True)
            
            model_name = "google/flan-t5-base"
            
            logger.info("Loading...")
            
            self.tokenizer = T5Tokenizer.from_pretrained(
                model_name, 
                cache_dir=cache_dir
            )
            
            self.model = T5ForConditionalGeneration.from_pretrained(
                model_name,
                cache_dir=cache_dir
            )
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            logger.info(f"Model is already loaded，used by: {self.device}")
            
        except Exception as e:
            logger.error(f"Loading error：{str(e)}")
            raise Exception("Loading error, please try again")

    def generate_reply(self, original_email):
        try:
            # 构建详细的英文 prompt，包含具体的邮件结构指导
            prompt = f"""As the recipient, write a concise, professional reply to the following email:
            
            Guidelines:
            - Acknowledge the email.
            - Confirm participation or respond to specific requests.
            - Include a professional greeting and closing.

            Write your reply:"""
            
            with torch.no_grad():
                inputs = self.tokenizer(
                    prompt, 
                    return_tensors="pt", 
                    max_length=300, 
                    truncation=True,
                    padding=True
                )
                inputs = inputs.to(self.device)

                reply_ids = self.model.generate(
                    inputs["input_ids"],
                    max_length=350,            # 适当增加长度以容纳完整回复
                    min_length=100,            # 确保回复够详细
                    length_penalty=1.5,
                    num_beams=5,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    temperature=0.7,           # 保持较低温度以确保专业性
                    top_k=50,
                    top_p=0.9,
                    do_sample=False,
                    repetition_penalty=1.2,
                )

                reply = self.tokenizer.decode(reply_ids[0], skip_special_tokens=True)
                
                cleaned_reply = self.clean_reply(reply)
                formatted_reply = self.format_reply(cleaned_reply)
                
                return formatted_reply

        except Exception as e:
            logger.error(f"Email reply generation error: {str(e)}")
            raise Exception("Failed to generate email reply")

    def format_reply(self, reply):
        """Improve email formatting for professional appearance"""
        
        # 标准化问候语
        common_greetings = ['dear', 'hello', 'hi', 'greetings']
        if not any(reply.lower().startswith(greeting) for greeting in common_greetings):
            reply = "Dear [Name],\n\n" + reply

        # 标准化段落格式
        paragraphs = reply.split('\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para:
                # 确保段落结尾有适当的标点
                if not para.endswith(('.', '!', '?')):
                    para += '.'
                formatted_paragraphs.append(para)

        # 添加适当的段落间距
        reply = '\n\n'.join(formatted_paragraphs)

        # 标准化结束语
        common_closings = [
            'best regards',
            'kind regards',
            'sincerely',
            'best wishes',
            'regards',
            'yours truly',
            'yours sincerely'
        ]
        
        has_closing = any(closing in reply.lower() for closing in common_closings)
        
        if not has_closing:
            reply += "\n\nBest regards,\n[Your name]"

        # 确保签名完整
        if "[your name]" in reply.lower() and "[position]" not in reply.lower():
            reply += "\n[Position]\n[Organization]"

        return reply

    def clean_reply(self, reply):
        """Clean and polish the generated reply"""
        
        # 移除重复句子
        sentences = reply.split('.')
        unique_sentences = []
        seen = set()
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence.lower() not in seen:
                seen.add(sentence.lower())
                unique_sentences.append(sentence)
        
        # 重新组合句子
        reply = '. '.join(unique_sentences)
        if not reply.endswith('.'):
            reply += '.'

        # 移除可能的不当内容
        reply = reply.replace('AI language model', '')
        reply = reply.replace('as an AI', '')
        
        return reply

    def generate_summary(self, text):
        """生成郵件摘要"""
        try:
            prompt = f"""You are a friendly assistant helping users who don't understand the content.
            Help users quickly grasp the main ideas.
            Summarize the following text in a clear and concise way, and organize the key points into a list:
            {text.strip()}"""

            with torch.no_grad():
                inputs = self.tokenizer(
                    prompt, 
                    return_tensors="pt", 
                    max_length=1024, 
                    truncation=True,
                    padding=True
                )
                inputs = inputs.to(self.device)

                summary_ids = self.model.generate(
                    inputs["input_ids"],
                    max_length=150,
                    min_length=40,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    temperature=0.7
                )

                summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                return summary.strip()

        except Exception as e:
            logger.error(f"摘要生成錯誤：{str(e)}")
            raise Exception("摘要生成失敗")

# 初始化郵件生成器
email_generator = EmailGenerator()

@app.route('/reply', methods=['POST', 'OPTIONS'])
def generate_reply():
    logger.info(f"收到請求，方法：{request.method}")
    
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        logger.info(f"收到數據：{data}")
        
        if not data or 'content' not in data:
            return jsonify({"error": "缺少內容"}), 400
            
        content = data['content']
        
        # 添加輸入長度檢查
        if len(content.strip()) < 10:
            return jsonify({"error": "輸入內容太短"}), 400
        if len(content.strip()) > 5000:
            return jsonify({"error": "輸入內容超過限制"}), 400

        reply = email_generator.generate_reply(content)
        return jsonify({"reply": reply})
        
    except Exception as e:
        logger.error(f"錯誤：{str(e)}")
        return jsonify({"error": f"處理失敗：{str(e)}"}), 500

# 添加摘要生成的路由
@app.route('/summary', methods=['POST', 'OPTIONS'])
def generate_summary():
    logger.info(f"收到請求，方法：{request.method}")
    
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        logger.info(f"收到數據：{data}")
        
        if not data or 'content' not in data:
            return jsonify({"error": "缺少內容"}), 400
            
        content = data['content']
        
        # 添加輸入長度檢查
        if len(content.strip()) < 10:
            return jsonify({"error": "輸入內容太短"}), 400
        if len(content.strip()) > 5000:
            return jsonify({"error": "輸入內容超過限制"}), 400

        summary = email_generator.generate_summary(content)
        return jsonify({"summary": summary})
        
    except Exception as e:
        logger.error(f"錯誤：{str(e)}")
        return jsonify({"error": f"處理失敗：{str(e)}"}), 500

if __name__ == '__main__':
    print("啟動服務器...")
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    ) 
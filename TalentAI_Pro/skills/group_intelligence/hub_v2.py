"""
Group Intelligence Hub v2.0 - 多模态线索收集引擎
=================================================

核心功能：
1. 文本解析 - 结构化文本 → Candidate/Job
2. 图片解析 - 截图/照片 → 结构化数据（OCR + AI理解）
3. PDF解析 - PDF文件 → 结构化数据
4. 语音解析 - 语音 → 文本 → 结构化数据
5. 混合输入 - 多条信息融合

Skills协作入口：
- 输出 → JD Intelligence Engine v2.0
- 输出 → Candidate Intelligence Engine v2.0
- 输出 → Discovery Radar
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field


@dataclass
class ParsedCandidate:
    """解析后的候选人数据结构"""
    source: str = ""  # text/image/pdf/voice
    name: Optional[str] = None
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    years_experience: Optional[int] = None
    skills: List[str] = field(default_factory=list)
    education: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    salary_expectation: Optional[int] = None
    raw_text: str = ""
    confidence: float = 0.0
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedJob:
    """解析后的职位数据结构"""
    source: str = ""  # text/image/pdf/voice
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[tuple] = None  # (min, max)
    skills_required: List[str] = field(default_factory=list)
    experience_years: Optional[int] = None
    education_level: Optional[str] = None
    job_description: str = ""
    requirements: List[str] = field(default_factory=list)
    raw_text: str = ""
    confidence: float = 0.0
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class GroupIntelligenceHubV2:
    """
    Group Intelligence Hub v2.0
    多模态线索收集引擎

    输入格式：
    - 文本 (str): 直接文本、聊天记录、邮件正文
    - 图片 (str/bytes): Base64或文件路径，支持简历截图/Job截图
    - PDF (str/bytes): PDF文件路径或字节数据
    - 语音 (str/bytes): 录音文件路径或Base64

    输出：
    - ParsedCandidate / ParsedJob 结构化数据
    - 可直接传入 JD Intelligence / Candidate Intelligence
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.supported_formats = {
            'text': ['txt', 'md', 'html', 'email', 'chat'],
            'image': ['jpg', 'jpeg', 'png', 'webp', 'gif'],
            'pdf': ['pdf'],
            'voice': ['mp3', 'wav', 'm4a', 'ogg', 'aac']
        }
        self._init_parsers()

    def _init_parsers(self):
        """初始化各类型解析器"""
        # 文本解析器 - 基于正则的快速解析
        self.text_parser = TextParser()

        # 图片解析器 - OCR + AI理解
        self.image_parser = ImageParser(config=self.config.get('image_parser'))

        # PDF解析器 - 文本提取 + AI理解
        self.pdf_parser = PDFParser(config=self.config.get('pdf_parser'))

        # 语音解析器 - 语音转文字 + NLP
        self.voice_parser = VoiceParser(config=self.config.get('voice_parser'))

    # ==================== 公开接口 ====================

    def parse_candidate(
        self,
        content: Union[str, bytes],
        source_type: str = "text",
        metadata: Optional[Dict] = None
    ) -> ParsedCandidate:
        """
        解析候选人信息

        Args:
            content: 输入内容
            source_type: text/image/pdf/voice
            metadata: 附加元数据

        Returns:
            ParsedCandidate
        """
        metadata = metadata or {}
        start_time = datetime.now()

        try:
            if source_type == "text":
                result = self._parse_text_candidate(content)
            elif source_type == "image":
                result = self._parse_image_candidate(content)
            elif source_type == "pdf":
                result = self._parse_pdf_candidate(content)
            elif source_type == "voice":
                result = self._parse_voice_candidate(content)
            else:
                raise ValueError(f"Unsupported source_type: {source_type}")

            result.source = source_type
            result.metadata = {
                **metadata,
                'parse_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'parser_version': 'v2.0'
            }

            return result

        except Exception as e:
            # 容错返回
            return ParsedCandidate(
                source=source_type,
                raw_text=str(content)[:500],
                warnings=[f"解析失败: {str(e)}"],
                confidence=0.0
            )

    def parse_job(
        self,
        content: Union[str, bytes],
        source_type: str = "text",
        metadata: Optional[Dict] = None
    ) -> ParsedJob:
        """
        解析职位信息

        Args:
            content: 输入内容
            source_type: text/image/pdf/voice
            metadata: 附加元数据

        Returns:
            ParsedJob
        """
        metadata = metadata or {}
        start_time = datetime.now()

        try:
            if source_type == "text":
                result = self._parse_text_job(content)
            elif source_type == "image":
                result = self._parse_image_job(content)
            elif source_type == "pdf":
                result = self._parse_pdf_job(content)
            elif source_type == "voice":
                result = self._parse_voice_job(content)
            else:
                raise ValueError(f"Unsupported source_type: {source_type}")

            result.source = source_type
            result.metadata = {
                **metadata,
                'parse_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'parser_version': 'v2.0'
            }

            return result

        except Exception as e:
            return ParsedJob(
                source=source_type,
                raw_text=str(content)[:500],
                warnings=[f"解析失败: {str(e)}"],
                confidence=0.0
            )

    def parse_batch(
        self,
        items: List[Dict]
    ) -> Dict[str, List]:
        """
        批量解析

        Args:
            items: [{"type": "candidate/job", "content": ..., "source_type": ...}, ...]

        Returns:
            {"candidates": [...], "jobs": [...]}
        """
        results = {"candidates": [], "jobs": []}

        for item in items:
            item_type = item.get("type", "candidate")
            content = item.get("content")
            source_type = item.get("source_type", "text")
            metadata = item.get("metadata", {})

            if item_type == "candidate":
                parsed = self.parse_candidate(content, source_type, metadata)
                results["candidates"].append(parsed)
            elif item_type == "job":
                parsed = self.parse_job(content, source_type, metadata)
                results["jobs"].append(parsed)

        return results

    # ==================== 内部解析方法 ====================

    def _parse_text_candidate(self, text: str) -> ParsedCandidate:
        """文本 → 候选人"""
        return self.text_parser.parse_candidate(text)

    def _parse_text_job(self, text: str) -> ParsedJob:
        """文本 → 职位"""
        return self.text_parser.parse_job(text)

    def _parse_image_candidate(self, content: Union[str, bytes]) -> ParsedCandidate:
        """图片 → 候选人"""
        # 模拟OCR + AI理解
        # 实际实现会调用OCR API（如百度OCR/腾讯OCR）或本地OCR
        ocr_text = self.image_parser.extract_text(content)
        return self.text_parser.parse_candidate(ocr_text)

    def _parse_image_job(self, content: Union[str, bytes]) -> ParsedJob:
        """图片 → 职位"""
        ocr_text = self.image_parser.extract_text(content)
        return self.text_parser.parse_job(ocr_text)

    def _parse_pdf_candidate(self, content: Union[str, bytes]) -> ParsedCandidate:
        """PDF → 候选人"""
        # 模拟PDF文本提取
        # 实际实现会使用PyPDF2/pdfplumber
        pdf_text = self.pdf_parser.extract_text(content)
        return self.text_parser.parse_candidate(pdf_text)

    def _parse_pdf_job(self, content: Union[str, bytes]) -> ParsedJob:
        """PDF → 职位"""
        pdf_text = self.pdf_parser.extract_text(content)
        return self.text_parser.parse_job(pdf_text)

    def _parse_voice_candidate(self, content: Union[str, bytes]) -> ParsedCandidate:
        """语音 → 候选人"""
        # 模拟语音转文字
        # 实际实现会调用语音识别API（如阿里ASR/腾讯ASR）
        text = self.voice_parser.speech_to_text(content)
        result = self.text_parser.parse_candidate(text)
        result.warnings.append("语音识别可能存在误差，建议人工确认")
        return result

    def _parse_voice_job(self, content: Union[str, bytes]) -> ParsedJob:
        """语音 → 职位"""
        text = self.voice_parser.speech_to_text(content)
        result = self.text_parser.parse_job(text)
        result.warnings.append("语音识别可能存在误差，建议人工确认")
        return result


# ==================== 子解析器 ====================

class TextParser:
    """文本解析器 - 基于正则的快速解析"""

    # 姓名检测模式
    NAME_PATTERNS = [
        r'^([A-Z][a-z]+ [A-Z][a-z]+)',  # 英文名 John Smith
        r'姓名[：:]\s*([^\n]+)',  # 中文姓名
        r'^([\u4e00-\u9fa5]{2,4})$',  # 单独一行中文名
        r'我叫([\u4e00-\u9fa5]{2,4})',  # 我叫XXX
        r'名叫([\u4e00-\u9fa5]{2,4})',  # 名叫XXX
        r'是([\u4e00-\u9fa5]{2,4})(?:，|。|$)',  # 是XXX，/ 是XXX。
    ]

    # 邮箱模式
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    # 电话模式
    PHONE_PATTERNS = [
        r'1[3-9]\d{9}',  # 中国手机号
        r'\+86\s*1[3-9]\d{9}',  # +86手机号
        r'\d{3,4}[-\s]?\d{7,8}',  # 固定电话
    ]

    # 公司/职位模式
    TITLE_COMPANY_PATTERNS = [
        r'职位[:\s]*([^\n，,]+)',  # 职位: XXX
        r'Title[:\s]*([^\n，,]+)',  # Title: XXX
        r'(?:现任|目前)(?:职位)?[:\s]*([^\n，,]+?)[@人在（(](.+?)[)）]',  # 现任XXX@XXX公司
        r'([^\n，,]{2,20})(?:@|在|职于|任职于|工作于)\s*([^\n，,]{2,30})公司',  # XXX在XXX公司
        r'公司[:\s]*([^\n，,]+)',  # 公司: XXX
    ]

    # 技能模式
    SKILL_PATTERNS = [
        r'技能[:\s]*([\s\S]+?)(?:经历|经验|学历|$)',
        r'技术[:\s]*([\s\S]+?)(?:经历|经验|学历|$)',
        r'(?:skills|technologies)[:\s]*([\s\S]+?)(?:experience|education|$)',
    ]

    # 经验年限模式
    YEARS_PATTERNS = [
        r'(\d+)\+?\s*年',
        r'(\d+)\+?\s*years?',
        r'(\d+)\s*yrs?',
    ]

    # 薪资模式
    SALARY_PATTERNS = [
        r'期望薪资[:\s]*(\d+)[kK~-](\d+)[kK]?',
        r'薪资[:\s]*(\d+)[kK]?(?:~|\-|至)(\d+)[kK]?',
        r'(?:salary|expecting)[:\s]*(\d+)[kK]?(?:~|\-|to)(\d+)[kK]?',
    ]

    # 学历模式
    EDUCATION_PATTERNS = [
        r'(博士|硕士|本科|大专|高中|中专)',
        r'(Ph\.?D\.?|Master|Bachelor|BS|MS|BA|MA)',
    ]

    def parse_candidate(self, text: str) -> ParsedCandidate:
        """解析候选人文本"""
        result = ParsedCandidate(raw_text=text)

        # 提取姓名
        for pattern in self.NAME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.name = match.group(1).strip()
                break

        # 提取联系方式
        email_match = re.search(self.EMAIL_PATTERN, text)
        if email_match:
            result.email = email_match.group(0)

        for pattern in self.PHONE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                result.phone = match.group(0)
                break

        # 提取公司/职位 - 分别处理，避免一个匹配就退出
        title_matched = False
        company_matched = False

        for pattern in self.TITLE_COMPANY_PATTERNS:
            if title_matched and company_matched:
                break
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups) >= 2 and not title_matched and not company_matched:
                    result.current_title = groups[0].strip()
                    result.current_company = groups[1].strip()
                    title_matched = True
                    company_matched = True
                elif len(groups) == 1:
                    if '公司' in pattern or 'Company' in pattern:
                        if not company_matched:
                            result.current_company = groups[0].strip()
                            company_matched = True
                    else:
                        if not title_matched:
                            result.current_title = groups[0].strip()
                            title_matched = True

        # 提取技能
        for pattern in self.SKILL_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                skills_text = match.group(1)
                # 分割技能列表
                skills = re.split(r'[,，、/、\|]', skills_text)
                result.skills = [s.strip() for s in skills if s.strip()][:20]
                break

        # 提取经验年限
        for pattern in self.YEARS_PATTERNS:
            match = re.search(pattern, text)
            if match:
                result.years_experience = int(match.group(1))
                break

        # 提取薪资期望
        for pattern in self.SALARY_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                min_sal = int(match.group(1))
                max_sal = int(match.group(2))
                result.salary_expectation = (min_sal + max_sal) // 2 * 1000  # 转为年薪
                break

        # 提取学历
        for pattern in self.EDUCATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.education = match.group(1)
                break

        # 提取LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/([\w-]+)', text, re.IGNORECASE)
        if linkedin_match:
            result.linkedin_url = f"https://linkedin.com/in/{linkedin_match.group(1)}"

        # 计算置信度
        result.confidence = self._calculate_confidence(result)

        return result

    def parse_job(self, text: str) -> ParsedJob:
        """解析职位文本"""
        result = ParsedJob(raw_text=text)

        # 提取职位名称
        title_patterns = [
            r'职位[：:]\s*([^\n]+)',
            r'(?:Job\s*Title?|Title|岗位)[:\s]*([^\n]+)',
            r'^(.{2,30})[:\s]*(?:职位|招聘|Job)',  # "高级Python工程师 职位"
        ]
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.title = match.group(1).strip()
                break

        # 提取公司名称
        company_patterns = [
            r'(?:公司|Company|雇主)[:\s]*([^\n，,]+)',
            r'([^\n，,]{2,20})\s*(?:有限公司|Inc\.|Corp\.|LLC|Ltd\.))',
        ]
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                result.company = match.group(1).strip()
                break

        # 提取地点
        location_patterns = [
            r'(?:地点|Location|城市|工作地)[:\s]*([^\n，,]+)',
            r'([北京上海广州深圳杭州南京苏州成都武汉西安]+)',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                result.location = match.group(1).strip()
                break

        # 提取薪资范围
        for pattern in self.SALARY_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                min_sal = int(match.group(1))
                max_sal = int(match.group(2))
                result.salary_range = (min_sal * 1000, max_sal * 1000)
                break

        # 提取技能要求
        for pattern in self.SKILL_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                skills_text = match.group(1)
                skills = re.split(r'[,，、/、\|]', skills_text)
                result.skills_required = [s.strip() for s in skills if s.strip()][:20]
                break

        # 提取经验要求
        for pattern in self.YEARS_PATTERNS:
            match = re.search(pattern, text)
            if match:
                result.experience_years = int(match.group(1))
                break

        # 提取学历要求
        for pattern in self.EDUCATION_PATTERNS:
            match = re.search(pattern, text)
            if match:
                result.education_level = match.group(1)
                break

        # 提取职位描述
        jd_patterns = [
            r'(?:职位描述|Job Description|JD|职责|Description)[:\s]*(.+?)(?:要求|Qualifications|技能|$)',
            r'(?:岗位职责|工作内容)[:\s]*(.+?)(?:要求|条件|$)',
        ]
        for pattern in jd_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                result.job_description = match.group(1).strip()[:2000]
                break

        # 如果没有找到独立描述，整个文本作为描述
        if not result.job_description:
            result.job_description = text[:2000]

        # 提取要求列表
        req_pattern = r'(?:要求| Qualifications|条件)[:\s]*\n+([\s\S]+?)$'
        match = re.search(req_pattern, text)
        if match:
            req_text = match.group(1)
            requirements = [r.strip() for r in re.split(r'[\n\r]+', req_text) if r.strip()]
            result.requirements = requirements[:10]

        # 计算置信度
        result.confidence = self._calculate_job_confidence(result)

        return result

    def _calculate_confidence(self, result: ParsedCandidate) -> float:
        """计算解析置信度"""
        score = 0.0
        if result.name: score += 0.2
        if result.email: score += 0.15
        if result.phone: score += 0.1
        if result.current_title: score += 0.15
        if result.current_company: score += 0.15
        if result.skills: score += 0.15
        if result.years_experience: score += 0.1
        return min(score, 1.0)

    def _calculate_job_confidence(self, result: ParsedJob) -> float:
        """计算职位解析置信度"""
        score = 0.0
        if result.title: score += 0.25
        if result.company: score += 0.2
        if result.location: score += 0.1
        if result.salary_range: score += 0.15
        if result.skills_required: score += 0.15
        if result.experience_years: score += 0.1
        if result.education_level: score += 0.05
        return min(score, 1.0)


class ImageParser:
    """图片解析器 - OCR + AI理解"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._ocr_available = None

    def _check_ocr(self):
        """检查OCR能力"""
        if self._ocr_available is None:
            # 模拟检测 - 实际应检测百度OCR/腾讯OCR/API可用性
            self._ocr_available = True
        return self._ocr_available

    def extract_text(self, content: Union[str, bytes]) -> str:
        """
        从图片提取文本

        Args:
            content: 图片路径/URL/Base64/字节数据

        Returns:
            提取的文本
        """
        if not self._check_ocr():
            return "[OCR不可用]"

        # 模拟OCR处理
        # 实际实现:
        # 1. 如果是文件路径: 使用 Pillow 打开并转为Base64
        # 2. 调用OCR API (百度/腾讯/阿里)
        # 3. 返回识别的文本

        if isinstance(content, str):
            # 假设是Base64或路径
            if content.startswith('data:image') or len(content) > 1000:
                # Base64图片
                return self._mock_ocr_result("[图片OCR结果]")
            elif content.endswith(('.jpg', '.png', '.jpeg')):
                # 文件路径
                return self._mock_ocr_result(f"[图片文件: {content}]")
        elif isinstance(content, bytes):
            # 字节数据
            return self._mock_ocr_result("[二进制图片OCR结果]")

        return "[无法解析图片格式]"

    def _mock_ocr_result(self, source_info: str) -> str:
        """模拟OCR结果 - 实际应调用真实OCR"""
        return f"""
姓名: 张三
邮箱: zhangsan@example.com
电话: 13800138000
职位: 高级算法工程师
公司: 某知名互联网公司
技能: Python, TensorFlow, PyTorch, 机器学习, 深度学习
经验: 8年
学历: 硕士
"""


class PDFParser:
    """PDF解析器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

    def extract_text(self, content: Union[str, bytes]) -> str:
        """
        从PDF提取文本

        Args:
            content: PDF路径/字节数据

        Returns:
            提取的文本
        """
        # 模拟PDF处理
        # 实际实现使用 PyPDF2 / pdfplumber

        if isinstance(content, str) and content.endswith('.pdf'):
            # 文件路径
            return self._mock_pdf_result(f"[PDF文件: {content}]")
        elif isinstance(content, bytes):
            # 字节数据
            return self._mock_pdf_result("[二进制PDF数据]")
        return "[无法解析PDF格式]"

    def _mock_pdf_result(self, source_info: str) -> str:
        """模拟PDF解析结果"""
        return f"""
{source_info}

姓名: 李四
邮箱: lisi@example.com
电话: 13900139000
职位: 产品经理
公司: 某科技公司
技能: 产品设计, 需求分析, 项目管理, Axure, SQL
经验: 5年
学历: 本科
"""


class VoiceParser:
    """语音解析器 - 语音转文字"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._asr_available = None

    def _check_asr(self):
        """检查ASR能力"""
        if self._asr_available is None:
            # 模拟检测
            self._asr_available = True
        return self._asr_available

    def speech_to_text(self, content: Union[str, bytes]) -> str:
        """
        语音转文字

        Args:
            content: 音频文件路径/Base64/字节数据

        Returns:
            识别出的文本
        """
        if not self._check_asr():
            return "[语音识别不可用]"

        # 模拟ASR处理
        # 实际实现:
        # 1. 如果是文件: 直接发送
        # 2. 如果是Base64: 解码后发送
        # 3. 调用ASR API (阿里/腾讯/科大讯飞)

        if isinstance(content, str):
            if content.endswith(('.mp3', '.wav', '.m4a', '.ogg', '.aac')):
                return self._mock_asr_result(f"[音频文件: {content}]")
            else:
                # Base64
                return self._mock_asr_result("[Base64音频]")
        elif isinstance(content, bytes):
            return self._mock_asr_result("[二进制音频]")

        return "[无法解析音频格式]"

    def _mock_asr_result(self, source_info: str) -> str:
        """模拟ASR结果"""
        return f"""
{source_info}

我叫王五，今年32岁，现在在一家互联网公司做技术总监。
主要负责AI算法的研发，擅长Python和深度学习。
之前在华为工作过5年，有10年的工作经验。
硕士毕业于清华大学。
期望薪资大概在80K到100K每月。
"""


# ==================== Skills协作入口 ====================

class SkillsIntegration:
    """
    Skills协作入口

    提供与下游Skills的集成接口：
    - JD Intelligence Engine v2.0
    - Candidate Intelligence Engine v2.0
    - Discovery Radar
    - Matching Engine v2
    - Smart Outreach Engine
    - Deal Tracker
    """

    def __init__(self, hub: GroupIntelligenceHubV2):
        self.hub = hub
        self._skills_ready = {
            'jd_intelligence': False,
            'candidate_intelligence': False,
            'discovery_radar': False,
            'matching_engine': False,
            'smart_outreach': False,
            'deal_tracker': False
        }

    def connect_skill(self, skill_name: str, skill_instance: Any):
        """连接下游Skill"""
        if skill_name in self._skills_ready:
            setattr(self, skill_name, skill_instance)
            self._skills_ready[skill_name] = True

    def is_ready(self) -> Dict[str, bool]:
        """检查各Skill连接状态"""
        return self._skills_ready.copy()

    def pipeline_candidate(
        self,
        content: Union[str, bytes],
        source_type: str = "text",
        run_discovery: bool = True,
        run_matching: bool = True,
        run_outreach: bool = False
    ) -> Dict[str, Any]:
        """
        候选人完整处理流程

        Flow:
        Group Intelligence Hub → Candidate Intelligence → Discovery Radar → Matching → Outreach
        """
        # Step 1: 解析
        parsed = self.hub.parse_candidate(content, source_type)

        results = {
            'parsed_candidate': parsed,
            'candidate_intelligence': None,
            'discovery': None,
            'matching': None,
            'outreach': None
        }

        # Step 2: Candidate Intelligence
        if self._skills_ready.get('candidate_intelligence'):
            results['candidate_intelligence'] = self.hub.candidate_intelligence.analyze(parsed)

        # Step 3: Discovery Radar
        if run_discovery and self._skills_ready.get('discovery_radar'):
            results['discovery'] = self.hub.discovery_radar.investigate(parsed.name, parsed.current_company)

        # Step 4: Matching (需要Job数据，这里仅返回 enriched candidate)
        if run_matching and self._skills_ready.get('matching_engine'):
            # 需要Job数据才能匹配
            pass

        # Step 5: Outreach
        if run_outreach and self._skills_ready.get('smart_outreach'):
            if results.get('discovery') or results.get('candidate_intelligence'):
                outreach_input = {
                    'candidate': parsed,
                    'intelligence': results.get('candidate_intelligence'),
                    'discovery': results.get('discovery')
                }
                results['outreach'] = self.hub.smart_outreach.generate(outreach_input)

        return results

    def pipeline_job(
        self,
        content: Union[str, bytes],
        source_type: str = "text",
        run_intelligence: bool = True,
        run_matching: bool = True
    ) -> Dict[str, Any]:
        """
        职位完整处理流程

        Flow:
        Group Intelligence Hub → JD Intelligence → Matching
        """
        # Step 1: 解析
        parsed = self.hub.parse_job(content, source_type)

        results = {
            'parsed_job': parsed,
            'jd_intelligence': None,
            'matching': None
        }

        # Step 2: JD Intelligence
        if run_intelligence and self._skills_ready.get('jd_intelligence'):
            results['jd_intelligence'] = self.hub.jd_intelligence.analyze(parsed)

        # Step 3: Matching (需要Candidate数据)
        if run_matching and self._skills_ready.get('matching_engine'):
            # 需要Candidate数据才能匹配
            pass

        return results


# ==================== 便捷函数 ====================

def create_hub(config: Optional[Dict] = None) -> GroupIntelligenceHubV2:
    """创建Group Intelligence Hub v2实例"""
    return GroupIntelligenceHubV2(config=config)


def quick_parse_candidate(text: str) -> ParsedCandidate:
    """快速解析候选人文本"""
    hub = GroupIntelligenceHubV2()
    return hub.parse_candidate(text, source_type="text")


def quick_parse_job(text: str) -> ParsedJob:
    """快速解析职位文本"""
    hub = GroupIntelligenceHubV2()
    return hub.parse_job(text, source_type="text")
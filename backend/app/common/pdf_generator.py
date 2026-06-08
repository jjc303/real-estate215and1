"""PDF 生成工具：合同和账单下载。"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from io import BytesIO

from fpdf import FPDF


class ContractPDF(FPDF):
    """合同 PDF 模板。"""

    def __init__(self) -> None:
        super().__init__()
        self._setup_font()

    def _setup_font(self) -> None:
        paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttf",
        ]
        for p in paths:
            if __import__("os").path.isfile(p):
                self.add_font("simfang", "", p, uni=True)
                self.add_font("simfang", "B", p, uni=True)
                return
        raise FileNotFoundError("Chinese font not found. Install fonts-wqy-microhei.")

    def header(self) -> None:
        self.set_font("simfang", "", 24)
        self.cell(0, 15, "房屋租赁合同", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("simfang", "", 8)
        self.cell(0, 10, f"第 {self.page_no()} 页", align="C")


class BillPDF(FPDF):
    """账单 PDF 模板。"""

    def __init__(self) -> None:
        super().__init__()
        self._setup_font()

    def _setup_font(self) -> None:
        paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttf",
        ]
        for p in paths:
            if __import__("os").path.isfile(p):
                self.add_font("simfang", "", p, uni=True)
                self.add_font("simfang", "B", p, uni=True)
                return
        raise FileNotFoundError("Chinese font not found. Install fonts-wqy-microhei.")

    def header(self) -> None:
        self.set_font("simfang", "", 24)
        self.cell(0, 15, "缴费账单", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("simfang", "", 8)
        self.cell(0, 10, f"第 {self.page_no()} 页", align="C")


def _section_label(pdf: FPDF, label: str) -> None:
    pdf.set_font("simfang", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, label, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)


def _field_row(pdf: FPDF, label: str, value: str) -> None:
    pdf.set_font("simfang", "", 11)
    pdf.cell(50, 8, label, align="R")
    pdf.cell(5, 8, "")
    pdf.set_font("simfang", "", 11)
    pdf.cell(0, 8, value, new_x="LMARGIN", new_y="NEXT")


def _separator(pdf: FPDF) -> None:
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)


STATUS_LABEL_MAP: dict[str, str] = {
    "unpaid": "未支付",
    "paid": "已支付",
    "cancelled": "已取消",
    "overdue": "已逾期",
    "pending": "待确认",
    "active": "生效中",
    "rejected": "已拒绝",
    "terminated": "已终止",
    "draft": "草稿",
    "listed": "已上架",
    "offline": "已下架",
    "rented": "已出租",
    "maintenance": "维修中",
}


def _status_label(status: str) -> str:
    return STATUS_LABEL_MAP.get(status, status)


def build_contract_pdf(
    contract_id: int,
    *,
    house_title: str,
    house_address: str,
    house_type: str,
    house_area: Decimal,
    landlord_name: str,
    tenant_name: str,
    monthly_rent: Decimal,
    deposit: Decimal,
    start_date: date,
    end_date: date,
    status: str,
    created_at: str,
) -> bytes:
    pdf = ContractPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    _section_label(pdf, "基本信息")
    _field_row(pdf, "合同编号：", f"#{contract_id}")
    _field_row(pdf, "签订日期：", created_at)
    _field_row(pdf, "合同状态：", _status_label(status))
    _separator(pdf)

    _section_label(pdf, "合同双方")
    _field_row(pdf, "出租方（甲方）：", landlord_name)
    _field_row(pdf, "承租方（乙方）：", tenant_name)
    _separator(pdf)

    _section_label(pdf, "房屋信息")
    _field_row(pdf, "房源名称：", house_title)
    _field_row(pdf, "地址：", house_address)
    _field_row(pdf, "户型：", house_type)
    _field_row(pdf, "面积：", f"{house_area} ㎡")
    _separator(pdf)

    _section_label(pdf, "租约信息")
    _field_row(pdf, "月租金：", f"¥{monthly_rent}")
    _field_row(pdf, "押金：", f"¥{deposit}")
    _field_row(pdf, "起租日期：", str(start_date))
    _field_row(pdf, "终止日期：", str(end_date))
    _separator(pdf)

    pdf.set_font("simfang", "", 10)
    pdf.multi_cell(0, 6, "条款：\n1. 甲方保证拥有该房屋的合法出租权。\n2. 乙方应按约定时间支付租金，逾期按日收取滞纳金。\n3. 租赁期间房屋自然损耗由甲方负责维修。\n4. 乙方不得擅自转租或改变房屋用途。\n5. 双方提前终止合同需提前 30 日书面通知。\n6. 本合同一式两份，双方各执一份，具有同等法律效力。")
    _separator(pdf)

    pdf.ln(10)
    _field_row(pdf, "甲方签字：________________", "")
    _field_row(pdf, "乙方签字：________________", "")
    _field_row(pdf, "签订日期：________________", "")

    return pdf.output()


def build_bill_pdf(
    bill_id: int,
    *,
    house_title: str,
    bill_type: str,
    amount: Decimal,
    due_date: date,
    status: str,
    created_at: str,
) -> bytes:
    pdf = BillPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    _section_label(pdf, "基本信息")
    _field_row(pdf, "账单编号：", f"#{bill_id}")
    _field_row(pdf, "创建日期：", created_at)
    _separator(pdf)

    _section_label(pdf, "账单明细")
    _field_row(pdf, "房源：", house_title)
    _field_row(pdf, "类型：", bill_type)
    _field_row(pdf, "金额：", f"¥{amount}")
    _field_row(pdf, "到期日：", str(due_date))
    _field_row(pdf, "状态：", _status_label(status))

    return pdf.output()

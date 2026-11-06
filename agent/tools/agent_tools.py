from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random
import os
from utils.logger_handler import logger
from utils.config_handler import agent_config
from utils.path_tool import get_abs_path

rag = RagSummarizeService()

# -----------------------------
# 模拟店铺、时间范围、预警/指标/交易/供应链数据
# 后续可替换为真实数据接口（生意参谋 / 订单中台 / 物流平台等）
# -----------------------------

shop_list = [
    "潮流服饰旗舰店",
    "数码家电专营店",
    "美妆个护旗舰店",
    "食品生鲜专营店",
    "母婴用品旗舰店",
]

time_range_list = [
    "最近1小时",
    "最近24小时",
    "今天",
    "本周",
    "本月",
]

mock_alert_data = {
    "潮流服饰旗舰店": {
        "最近1小时": {
            "critical": 2,
            "warning": 4,
            "alerts": [
                "爆款卫衣 SKU 库存售罄预警",
                "直播间流量转化率骤降 42%",
                "退款率短时冲高至 8.7%",
            ],
        },
        "今天": {
            "critical": 4,
            "warning": 9,
            "alerts": [
                "爆款卫衣 SKU 库存售罄预警",
                "直播间流量转化率骤降",
                "优惠券核销失败率异常升高",
                "加购率低于大促预期",
            ],
        },
        "本月": {
            "critical": 12,
            "warning": 28,
            "alerts": [
                "多个爆款 SKU 出现库存售罄",
                "大促期间转化率波动明显",
                "退款率多次突破预警线",
                "物流发货延迟投诉增多",
            ],
        },
    },
    "数码家电专营店": {
        "最近1小时": {
            "critical": 1,
            "warning": 3,
            "alerts": [
                "分期支付通道失败率升高",
                "大件商品发货延迟预警",
            ],
        },
        "今天": {
            "critical": 3,
            "warning": 6,
            "alerts": [
                "分期支付通道失败率升高",
                "大件商品发货延迟预警",
                "价保申请量异常增多",
            ],
        },
        "本月": {
            "critical": 9,
            "warning": 21,
            "alerts": [
                "分期支付通道多次波动",
                "大件物流时效不达标",
                "高价商品转化率持续低于预期",
                "价保与退换货申请量增多",
            ],
        },
    },
    "食品生鲜专营店": {
        "最近1小时": {
            "critical": 2,
            "warning": 3,
            "alerts": [
                "冷链配送温控异常预警",
                "化冻变质类差评集中出现",
            ],
        },
        "今天": {
            "critical": 3,
            "warning": 7,
            "alerts": [
                "冷链配送温控异常预警",
                "生鲜商品损耗率超标",
                "缺货退款订单增多",
            ],
        },
        "本月": {
            "critical": 10,
            "warning": 23,
            "alerts": [
                "冷链温控异常多次发生",
                "生鲜损耗率连续超标",
                "化冻变质类差评率升高",
                "部分 SKU 缺货退款集中",
            ],
        },
    },
}

mock_metric_data = {
    "潮流服饰旗舰店": {
        "最近1小时": {
            "gmv": "¥426,800",
            "order_count": "4,863",
            "avg_order_value": "¥87.8",
            "conversion_rate": "2.1%",
            "uv": "231,400",
            "refund_rate": "8.7%",
            "add_to_cart_rate": "11.2%",
        },
        "今天": {
            "gmv": "¥3,865,000",
            "order_count": "42,150",
            "avg_order_value": "¥91.7",
            "conversion_rate": "2.6%",
            "uv": "1,621,000",
            "refund_rate": "7.4%",
            "add_to_cart_rate": "12.8%",
        },
        "本月": {
            "gmv": "¥86,420,000",
            "order_count": "912,300",
            "avg_order_value": "¥94.7",
            "conversion_rate": "3.1%",
            "uv": "29,430,000",
            "refund_rate": "5.8%",
            "add_to_cart_rate": "13.6%",
        },
    },
    "数码家电专营店": {
        "最近1小时": {
            "gmv": "¥1,286,000",
            "order_count": "1,731",
            "avg_order_value": "¥742.9",
            "conversion_rate": "1.4%",
            "uv": "123,600",
            "refund_rate": "3.2%",
            "add_to_cart_rate": "6.8%",
        },
        "今天": {
            "gmv": "¥9,642,000",
            "order_count": "12,840",
            "avg_order_value": "¥750.9",
            "conversion_rate": "1.6%",
            "uv": "802,500",
            "refund_rate": "2.9%",
            "add_to_cart_rate": "7.4%",
        },
        "本月": {
            "gmv": "¥216,380,000",
            "order_count": "286,400",
            "avg_order_value": "¥755.5",
            "conversion_rate": "1.9%",
            "uv": "15,073,000",
            "refund_rate": "2.4%",
            "add_to_cart_rate": "8.1%",
        },
    },
    "食品生鲜专营店": {
        "最近1小时": {
            "gmv": "¥356,000",
            "order_count": "8,922",
            "avg_order_value": "¥39.9",
            "conversion_rate": "4.6%",
            "uv": "193,900",
            "refund_rate": "5.9%",
            "add_to_cart_rate": "15.3%",
        },
        "今天": {
            "gmv": "¥2,984,000",
            "order_count": "72,460",
            "avg_order_value": "¥41.2",
            "conversion_rate": "5.1%",
            "uv": "1,420,700",
            "refund_rate": "5.2%",
            "add_to_cart_rate": "16.7%",
        },
        "本月": {
            "gmv": "¥68,540,000",
            "order_count": "1,618,900",
            "avg_order_value": "¥42.3",
            "conversion_rate": "5.6%",
            "uv": "28,908,000",
            "refund_rate": "4.1%",
            "add_to_cart_rate": "17.9%",
        },
    },
}

mock_transaction_data = {
    "潮流服饰旗舰店": {
        "最近1小时": {
            "top_issues": [
                "库存超卖：爆款卫衣 SKU-8821 超卖 137 单",
                "优惠券核销失败：满300减50券核销失败率 6.2%",
                "支付失败：微信支付失败率升至 3.8%",
            ],
            "summary": "最近1小时店铺交易异常集中在爆款商品超卖、优惠券核销失败与支付失败三类，预计影响约 2,100 笔订单，建议优先核查库存同步与大促券配置。",
        },
        "今天": {
            "top_issues": [
                "库存超卖：多个爆款 SKU 出现超卖",
                "下单未支付超时取消单量升高",
                "优惠券核销失败率异常",
            ],
            "summary": "今日交易异常以爆款超卖和订单超时取消为主，优惠券核销问题集中在直播间发放的大额券。",
        },
        "本月": {
            "top_issues": [
                "大促高峰期库存同步延迟导致超卖",
                "退款申请集中在尺码不合适与色差问题",
                "支付失败与订单取消率阶段性升高",
            ],
            "summary": "本月交易异常主要发生在大促高峰期，超卖与退款问题突出，尺码与色差类退款占比最高。",
        },
    },
    "数码家电专营店": {
        "最近1小时": {
            "top_issues": [
                "分期支付通道超时：花呗分期失败率 5.4%",
                "大件物流揽收超时订单 86 笔",
            ],
            "summary": "最近1小时异常集中在分期支付通道超时与大件商品揽收延迟，涉及订单客单价高，需优先跟进。",
        },
        "今天": {
            "top_issues": [
                "分期支付通道多次超时",
                "价保申请集中爆发（降价 200 元以上商品）",
                "大件物流揽收超时",
            ],
            "summary": "今日异常以分期支付通道不稳定和价保申请增多为主，与部分商品调价直接相关。",
        },
        "本月": {
            "top_issues": [
                "分期支付通道月度波动 6 次",
                "大件物流时效不达标率 4.3%",
                "退换货以七天无理由与功能不符为主",
            ],
            "summary": "本月异常主要来源于外部分期支付通道波动与大件物流时效问题，整体客诉率可控。",
        },
    },
    "食品生鲜专营店": {
        "最近1小时": {
            "top_issues": [
                "冷链配送温控超标订单 143 笔",
                "化冻变质类差评新增 27 条",
            ],
            "summary": "最近1小时异常集中在冷链配送温控超标，伴随化冻变质差评增多，需立即核查涉事批次与配送线路。",
        },
        "今天": {
            "top_issues": [
                "冷链温控超标集中在华东线路",
                "缺货退款订单 312 笔",
                "生鲜损耗率升至 7.8%",
            ],
            "summary": "今日异常以华东线路冷链温控问题为主，缺货退款增多与部分 SKU 备货不足有关。",
        },
        "本月": {
            "top_issues": [
                "冷链温控异常月度发生 14 次",
                "化冻变质差评率 1.9%",
                "大促备货不足导致缺货退款集中",
            ],
            "summary": "本月异常主要由冷链运输稳定性不足与大促备货预测偏差造成，差评与损耗双重承压。",
        },
    },
}

mock_supply_chain_data = {
    "潮流服饰旗舰店": {
        "upstream_suppliers": ["广州服装产业带供应商", "杭州面辅料供应商"],
        "sales_channels": ["直播间", "平台搜索推荐", "会员私域", "大促会场"],
        "fulfillment": ["华东中心仓", "华南前置仓", "顺丰速运", "微信支付", "支付宝"],
    },
    "数码家电专营店": {
        "upstream_suppliers": ["品牌厂商直供", "华南 3C 产业带供应商"],
        "sales_channels": ["平台搜索推荐", "品牌直播", "企业采购通道"],
        "fulfillment": ["全国中心仓", "京东物流", "德邦大件物流", "花呗分期", "银联支付"],
    },
    "食品生鲜专营店": {
        "upstream_suppliers": ["山东果蔬基地", "舟山海鲜产地直采", "内蒙古牧场直供"],
        "sales_channels": ["平台搜索推荐", "会员日专场", "社区团购"],
        "fulfillment": ["华东冷链仓", "华南冷链仓", "顺丰冷运", "微信支付"],
    },
    "美妆个护旗舰店": {
        "upstream_suppliers": ["品牌方一级代理", "保税仓直供"],
        "sales_channels": ["达人直播", "平台搜索推荐", "会员私域"],
        "fulfillment": ["保税仓", "华东中心仓", "中通快递", "支付宝"],
    },
    "母婴用品旗舰店": {
        "upstream_suppliers": ["品牌厂商直供", "进口奶粉保税渠道"],
        "sales_channels": ["平台搜索推荐", "母婴频道", "会员私域"],
        "fulfillment": ["全国中心仓", "保税仓", "京东物流", "支付宝", "微信支付"],
    },
}


# RAG 工具：保留
@tool(description="从向量存储中检索电商运营知识、平台规则、大促活动方案、运营SOP等参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)



# 基础上下文工具
@tool(description="获取当前待分析的目标店铺名称，以纯字符串形式返回")
def get_target_shop() -> str:
    return random.choice(shop_list)


@tool(description="获取当前分析任务的默认时间范围，以纯字符串形式返回，例如最近1小时、今天、本周、本月")
def get_time_range() -> str:
    return random.choice(time_range_list)


# 预警 / 指标 / 交易 / 供应链工具
@tool(description="获取指定店铺在指定时间范围内的运营预警信息（库存售罄、转化率骤降、退款率异常等），以结构化字符串形式返回；若未检索到数据则返回空字符串")
def fetch_operation_alerts(shop_name: str, time_range: str) -> str:
    try:
        data = mock_alert_data[shop_name][time_range]
        return str(data)
    except KeyError:
        logger.warning(f"[fetch_operation_alerts] 未检索到店铺 {shop_name} 在 {time_range} 的预警数据")
        return ""


@tool(description="获取指定店铺在指定时间范围内的核心经营指标（GMV、订单量、客单价、转化率、UV、退款率等），以结构化字符串形式返回；若未检索到数据则返回空字符串")
def fetch_sales_metrics(shop_name: str, time_range: str) -> str:
    try:
        data = mock_metric_data[shop_name][time_range]
        return str(data)
    except KeyError:
        logger.warning(f"[fetch_sales_metrics] 未检索到店铺 {shop_name} 在 {time_range} 的经营指标数据")
        return ""


@tool(description="获取指定店铺在指定时间范围内的交易异常摘要与高频问题（超卖、支付失败、核销异常等），以结构化字符串形式返回；若未检索到数据则返回空字符串")
def fetch_transaction_summary(shop_name: str, time_range: str) -> str:
    try:
        data = mock_transaction_data[shop_name][time_range]
        return str(data)
    except KeyError:
        logger.warning(f"[fetch_transaction_summary] 未检索到店铺 {shop_name} 在 {time_range} 的交易异常数据")
        return ""


@tool(description="获取指定店铺的上游供应商、销售渠道与履约配送链路信息，以结构化字符串形式返回；若未检索到数据则返回空字符串")
def fetch_supply_chain_topology(shop_name: str) -> str:
    try:
        data = mock_supply_chain_data[shop_name]
        return str(data)
    except KeyError:
        logger.warning(f"[fetch_supply_chain_topology] 未检索到店铺 {shop_name} 的供应链数据")
        return ""


# 报告工具
def generate_report_data():
    """
    预留函数：
    后续如果需要从真实外部系统拉取数据，
    可以在这里统一聚合 生意参谋 / 订单中台 / 物流跟踪平台 等数据。
    """
    return None


@tool(description="获取指定店铺在指定时间范围内的经营报告汇总数据，以结构化字符串形式返回；若未检索到数据则返回空字符串")
def fetch_report_data(shop_name: str, time_range: str) -> str:
    generate_report_data()

    try:
        alert_data = mock_alert_data.get(shop_name, {}).get(time_range, {})
        metric_data = mock_metric_data.get(shop_name, {}).get(time_range, {})
        transaction_data = mock_transaction_data.get(shop_name, {}).get(time_range, {})
        supply_chain_data = mock_supply_chain_data.get(shop_name, {})

        if not alert_data and not metric_data and not transaction_data:
            logger.warning(f"[fetch_report_data] 未检索到店铺 {shop_name} 在 {time_range} 的报告数据")
            return ""

        report_data = {
            "shop_name": shop_name,
            "time_range": time_range,
            "alert_summary": alert_data,
            "metric_summary": metric_data,
            "transaction_summary": transaction_data,
            "supply_chain_summary": supply_chain_data,
        }
        return str(report_data)
    except Exception as e:
        logger.error(f"[fetch_report_data] 获取店铺 {shop_name} 在 {time_range} 的报告数据失败：{str(e)}")
        return ""


@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成场景动态注入上下文信息，为后续提示词切换提供上下文信息")
def fill_context_for_report():
    return "fill_context_for_report已调用"

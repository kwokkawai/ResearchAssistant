"""
Interactive Shopify Agent
Handles conversational interaction with users to connect to Shopify API and query data
"""

from typing import Dict, Any, Optional
from datetime import datetime
import re
from agents.agent_manager import Agent
from integrations.shopify_api import get_shopify_client, test_connection

class ShopifyInteractiveAgent(Agent):
    """
    Interactive Shopify agent that guides users through authentication
    and handles Shopify API queries
    """
    
    def __init__(self, name: str = None, description: str = None, llm_manager = None):
        # Use provided name/description or defaults
        super().__init__(
            name=name or "shopify_interactive",
            description=description or "交互式Shopify助手，通过对话获取用户凭证并查询商店数据",
            llm_manager=llm_manager
        )
        self.session_credentials = {}  # Store credentials per session
        self.agent_definition = None  # Will be set by AgentManager
    
    @property
    def template_config(self):
        """Get template config from agent definition, resolving template_id if needed"""
        if self.agent_definition:
            from management.agent_manager import agent_manager as dynamic_agent_manager
            return dynamic_agent_manager.get_agent_template_config(self.agent_definition)
        return {}
    
    def get_specialization(self) -> str:
        return "shopify_integration"
    
    def is_authenticated(self, session_id: str) -> bool:
        """Check if session has valid Shopify credentials"""
        return session_id in self.session_credentials
    
    def set_credentials(self, session_id: str, shop_url: str, access_token: str) -> Dict[str, Any]:
        """
        Set and validate Shopify credentials for a session
        
        Args:
            session_id: Conversation session ID
            shop_url: Shopify shop URL
            access_token: API access token
            
        Returns:
            Connection test result
        """
        print(f"🔌 [Shopify] 正在测试连接到商店: {shop_url}")
        print(f"   Session ID: {session_id}")
        
        # Test the connection
        result = test_connection(shop_url, access_token)
        
        if result.get('success'):
            print(f"✅ [Shopify] 连接成功！")
            print(f"   商店名称: {result.get('shop_name')}")
            print(f"   商店域名: {result.get('shop_domain')}")
            print(f"   商店邮箱: {result.get('shop_email')}")
            print(f"   货币: {result.get('currency')}")
            print(f"   时区: {result.get('timezone')}")
            
            # Store credentials
            self.session_credentials[session_id] = {
                'shop_url': shop_url,
                'access_token': access_token,
                'shop_info': {
                    'name': result.get('shop_name'),
                    'domain': result.get('shop_domain'),
                    'email': result.get('shop_email'),
                    'currency': result.get('currency'),
                    'timezone': result.get('timezone')
                },
                'authenticated_at': datetime.now().isoformat()
            }
        else:
            print(f"❌ [Shopify] 连接失败: {result.get('message')}")
        
        return result
    
    def get_client(self, session_id: str) -> Optional[Any]:
        """Get configured Shopify client for session"""
        if session_id not in self.session_credentials:
            return None
        
        creds = self.session_credentials[session_id]
        return get_shopify_client(creds['shop_url'], creds['access_token'])
    
    def clear_credentials(self, session_id: str) -> bool:
        """Clear credentials for a session"""
        if session_id in self.session_credentials:
            del self.session_credentials[session_id]
            return True
        return False
    
    def detect_intent(self, query: str) -> Dict[str, Any]:
        """
        Detect user intent from query
        
        Returns dict with:
            - intent: str (auth, orders, fulfillments, transactions, customers, products, analysis, shop_info)
            - params: dict with extracted parameters
        """
        query_lower = query.lower()
        
        # Check for authentication intent
        if any(keyword in query_lower for keyword in ['配置', '设置', '连接', '登录', '认证', '凭证']):
            # Try to extract shop URL and token
            shop_url_match = re.search(r'([a-z0-9-]+\.myshopify\.com)', query)
            token_match = re.search(r'(shp[at]_[a-zA-Z0-9]{32})', query)
            
            return {
                'intent': 'auth',
                'params': {
                    'shop_url': shop_url_match.group(1) if shop_url_match else None,
                    'access_token': token_match.group(1) if token_match else None
                }
            }
        
        # Check for clear/logout intent
        if any(keyword in query_lower for keyword in ['清除', '退出', '登出', '断开']):
            return {'intent': 'logout', 'params': {}}
        
        # Check for order queries
        if any(keyword in query_lower for keyword in ['订单', 'order']):
            params = {'limit': 10}
            
            # Extract order ID (specific order number)
            order_id_match = re.search(r'订单[号id]*[\s:：]*(\d+)', query_lower)
            if order_id_match:
                params['order_id'] = int(order_id_match.group(1))
            
            # Extract explicit limit number (supports various formats)
            # Patterns: "5 orders", "last 5", "最近5个", "show 10", etc.
            limit_match = re.search(r'(?:last|latest|recent|show|display|get|最近|显示)\s*(\d+)|(\d+)\s*[个条]', query_lower)
            if limit_match:
                # Get the captured number (either from group 1 or 2)
                limit_num = limit_match.group(1) or limit_match.group(2)
                params['limit'] = min(int(limit_num), 250)
            elif any(keyword in query_lower for keyword in ['last', 'latest', 'recent', 'newest', '最后', '最新']):
                # Only if no explicit number and not searching for specific order ID
                if 'order_id' not in params:
                    params['limit'] = 1
            
            # Extract status
            if '待' in query_lower or 'pending' in query_lower:
                params['status'] = 'pending'
            elif '取消' in query_lower or 'cancel' in query_lower:
                params['status'] = 'cancelled'
            elif '完成' in query_lower or 'closed' in query_lower:
                params['status'] = 'closed'
            
            return {'intent': 'orders', 'params': params}
        
        # Check for fulfillment/shipping queries
        if any(keyword in query_lower for keyword in ['发货', '物流', 'fulfill', 'ship']):
            params = {}
            order_id_match = re.search(r'订单[号id]*[\s:：]*(\d+)', query_lower)
            if order_id_match:
                params['order_id'] = int(order_id_match.group(1))
            return {'intent': 'fulfillments', 'params': params}
        
        # Check for invoice/draft order queries
        if any(keyword in query_lower for keyword in ['发票', 'invoice', 'draft order', '草稿订单', '未完成订单']):
            params = {'limit': 10}
            
            # Extract specific draft order by name (e.g., "#D1", "D1", "#d1")
            # Shopify draft orders have names like "#D1", "#D2", etc.
            draft_name_match = re.search(r'#?[dD](\d+)', query)
            if draft_name_match:
                draft_num = draft_name_match.group(1)
                params['draft_order_name'] = f"#D{draft_num}"
                print(f"🔍 [Intent] 检测到发票名称: {params['draft_order_name']}")
            else:
                # Try to extract numeric ID (for direct API ID queries)
                draft_id_match = re.search(r'(?:发票|invoice|draft)[号id\s:：]*(\d{10,})', query_lower)
                if draft_id_match:
                    params['draft_order_id'] = int(draft_id_match.group(1))
                    print(f"🔍 [Intent] 检测到发票ID: {params['draft_order_id']}")
            
            # Extract status filter (only if no specific invoice is requested)
            if 'draft_order_name' not in params and 'draft_order_id' not in params:
                if any(keyword in query_lower for keyword in ['open', '未发送', '草稿']):
                    params['status'] = 'open'
                elif any(keyword in query_lower for keyword in ['sent', '已发送', 'invoice_sent']):
                    params['status'] = 'invoice_sent'
                elif any(keyword in query_lower for keyword in ['completed', '已完成', '已转换']):
                    params['status'] = 'completed'
                
                # Extract limit (only for list queries)
                limit_match = re.search(r'(?:last|latest|recent|show|display|get|最近|显示)\s*(\d+)|(\d+)\s*[个条]', query_lower)
                if limit_match:
                    limit_num = limit_match.group(1) or limit_match.group(2)
                    params['limit'] = min(int(limit_num), 250)
            
            return {'intent': 'invoices', 'params': params}
        
        # Check for transaction/billing queries
        if any(keyword in query_lower for keyword in ['账单', '交易', '支付', 'transaction', 'payment', 'billing']):
            params = {}
            order_id_match = re.search(r'订单[号id]*[\s:：]*(\d+)', query_lower)
            if order_id_match:
                params['order_id'] = int(order_id_match.group(1))
            return {'intent': 'transactions', 'params': params}
        
        # Check for customer queries
        if any(keyword in query_lower for keyword in ['客户', '用户', 'customer', 'user']):
            params = {'limit': 10}
            # Extract email or name for search
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', query)
            if email_match:
                params['search_query'] = email_match.group(1)
            return {'intent': 'customers', 'params': params}
        
        # Check for product queries
        if any(keyword in query_lower for keyword in ['产品', '商品', 'product', 'item']):
            params = {'limit': 10}
            return {'intent': 'products', 'params': params}
        
        # Check for analysis queries
        if any(keyword in query_lower for keyword in ['分析', '统计', '报告', 'analysis', 'report', 'statistics']):
            params = {'days': 30}
            days_match = re.search(r'(\d+)天', query_lower)
            if days_match:
                params['days'] = int(days_match.group(1))
            return {'intent': 'analysis', 'params': params}
        
        # Check for shop info queries
        if any(keyword in query_lower for keyword in ['商店信息', '店铺', 'shop', 'store info']):
            return {'intent': 'shop_info', 'params': {}}
        
        # Default: general query
        return {'intent': 'general', 'params': {}}
    
    def handle_auth_request(self, query: str, params: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle authentication request"""
        shop_url = params.get('shop_url')
        access_token = params.get('access_token')
        
        if shop_url and access_token:
            # Direct credentials provided
            result = self.set_credentials(session_id, shop_url, access_token)
            if result.get('success'):
                shop_info = self.session_credentials[session_id]['shop_info']
                return {
                    'response': f"✅ 成功连接到Shopify商店！\n\n"
                               f"商店名称: {shop_info['name']}\n"
                               f"商店域名: {shop_info['domain']}\n"
                               f"电子邮件: {shop_info['email']}\n"
                               f"货币: {shop_info['currency']}\n"
                               f"时区: {shop_info['timezone']}\n\n"
                               f"现在您可以开始查询订单、发货、账单等信息了。",
                    'authenticated': True,
                    'shop_info': shop_info
                }
            else:
                return {
                    'response': f"❌ 连接失败: {result.get('message')}\n\n"
                               f"请检查商店URL和访问令牌是否正确。",
                    'authenticated': False,
                    'error': result.get('message')
                }
        else:
            # Provide instructions
            return {
                'response': "要连接到您的Shopify商店，我需要以下信息：\n\n"
                           "1. **商店URL**: 例如 `your-shop.myshopify.com`\n"
                           "2. **访问令牌**: 从Shopify Admin API获取的访问令牌\n\n"
                           "请按以下格式提供：\n"
                           "```\n"
                           "商店URL: your-shop.myshopify.com\n"
                           "访问令牌: shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n"
                           "```\n\n"
                           "或者直接输入：\"配置商店 your-shop.myshopify.com shpat_xxxxx\"\n\n"
                           "**获取访问令牌的步骤：**\n"
                           "1. 登录Shopify管理后台\n"
                           "2. 进入「应用」>「应用和销售渠道」>「开发应用」\n"
                           "3. 创建自定义应用并配置API权限\n"
                           "4. 获取Admin API访问令牌",
                'authenticated': False,
                'awaiting_credentials': True
            }
    
    def handle_orders_query(self, params: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle orders query"""
        client = self.get_client(session_id)
        if not client:
            print(f"❌ [Shopify] 查询订单失败: 未认证")
            return {'error': '未认证', 'response': '请先配置Shopify凭证'}
        
        if 'order_id' in params:
            # Get specific order
            print(f"🔍 [Shopify] 查询订单详情: Order ID = {params['order_id']}")
            order_data = client.get_order(params['order_id'])
            if 'error' in order_data:
                print(f"❌ [Shopify] 查询订单失败: {order_data['error']}")
                return {'error': order_data['error'], 'response': f"查询订单失败: {order_data['error']}"}
            
            order = order_data.get('order', {})
            print(f"✅ [Shopify] 订单查询成功:")
            print(f"   订单号: #{order.get('name', order.get('id'))}")
            print(f"   总金额: {order.get('total_price')} {order.get('currency')}")
            print(f"   订单状态: {order.get('financial_status')}")
            print(f"   履行状态: {order.get('fulfillment_status') or '未发货'}")

            # 📋 Log API Response Data
            print(f"\n📦 [Shopify API Response] 订单详情:")
            print(f"      ID: {order.get('id')}")
            print(f"      Name: #{order.get('name')}")
            print(f"      Email: {order.get('email', 'N/A')}")
            print(f"      Total: {order.get('total_price')} {order.get('currency')}")
            print(f"      Financial Status: {order.get('financial_status')}")
            print(f"      Fulfillment Status: {order.get('fulfillment_status', 'N/A')}")
            print(f"      Line Items: {len(order.get('line_items', []))}")

            # 🔧 根据查询内容决定使用简洁格式还是详细格式
            if 'amount' in query.lower() or '金额' in query.lower() or 'total' in query.lower() or 'price' in query.lower():
                response = self._format_single_order_amount(order)
            else:
                response = self._format_order_details(order)
        else:
            # Get multiple orders
            print(f"🔍 [Shopify] 查询订单列表:")
            print(f"   状态筛选: {params.get('status') or '全部'}")
            print(f"   返回数量: {params.get('limit', 10)}")
            orders_data = client.get_orders(
                status=params.get('status'),
                limit=params.get('limit', 10)
            )
            if 'error' in orders_data:
                print(f"❌ [Shopify] 查询订单失败: {orders_data['error']}")
                return {'error': orders_data['error'], 'response': f"查询订单失败: {orders_data['error']}"}
            
            orders = orders_data.get('orders', [])
            print(f"✅ [Shopify] 订单列表查询成功:")
            print(f"   返回订单数: {len(orders)}")
            if orders:
                total_amount = sum(float(order.get('total_price', 0)) for order in orders)
                currency = orders[0].get('currency', 'USD')
                print(f"   总金额: {total_amount:.2f} {currency}")
                
            # 📋 Log API Response Data
            print(f"\n📦 [Shopify API Response] 订单数据:")
            import json
            for i, order in enumerate(orders[:5], 1):  # Show first 5 in log
                print(f"   Order {i}:")
                print(f"      ID: {order.get('id')}")
                print(f"      Name: #{order.get('name')}")
                print(f"      Total: {order.get('total_price')} {order.get('currency')}")
                print(f"      Status: {order.get('financial_status')}")
                print(f"      Customer: {order.get('customer', {}).get('email', 'N/A')}")
                print(f"      Created: {order.get('created_at', '')[:10]}")
            if len(orders) > 5:
                print(f"   ... and {len(orders) - 5} more orders")
            
            response = self._format_orders_list(orders, params.get('status'))
        
        # Include raw API data for LLM context
        return {
            'response': response, 
            'data': orders_data if 'orders_data' in locals() else order_data,
            'api_data': orders_data if 'orders_data' in locals() else order_data  # For LLM context
        }
    
    def _format_order_details(self, order: Dict[str, Any]) -> str:
        """Format single order details"""
        customer = order.get('customer', {})
        
        lines = [
            f"📦 订单详情",
            f"━━━━━━━━━━━━━━━━━━━━━━",
            f"订单号: #{order.get('name', order.get('id'))}",
            f"创建时间: {order.get('created_at', '').split('T')[0]}",
            f"订单状态: {order.get('financial_status', 'unknown')}",
            f"履行状态: {order.get('fulfillment_status') or '未发货'}",
            f"总金额: {order.get('total_price')} {order.get('currency')}",
            f"",
            f"👤 客户信息:",
            f"  姓名: {customer.get('first_name', '')} {customer.get('last_name', '')}",
            f"  邮箱: {customer.get('email', 'N/A')}",
            f"",
            f"📋 订单商品:"
        ]
        
        for item in order.get('line_items', []):
            lines.append(f"  • {item.get('title')} x{item.get('quantity')} - {item.get('price')} {order.get('currency')}")
        
        return "\n".join(lines)
    
    def _format_orders_list(self, orders: list, status: str = None) -> str:
        """Format list of orders"""
        if not orders:
            return f"未找到{'符合条件的' if status else ''}订单。"
        
        lines = [
            f"📦 订单列表 (共{len(orders)}个)",
            f"━━━━━━━━━━━━━━━━━━━━━━"
        ]
        
        for order in orders:
            customer = order.get('customer', {})
            customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or customer.get('email', 'Guest')
            
            lines.append(
                f"#{order.get('name')}: {order.get('total_price')} {order.get('currency')} | "
                f"{order.get('financial_status')} | {customer_name}"
            )
        
        return "\n".join(lines)
    
    def handle_invoice_query(self, params: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle invoice/draft order query"""
        client = self.get_client(session_id)
        if not client:
            print(f"❌ [Shopify] 查询发票失败: 未认证")
            return {'error': '未认证', 'response': '请先配置Shopify凭证'}
        
        # Handle query by draft order name (e.g., "#D1")
        if 'draft_order_name' in params:
            draft_name = params['draft_order_name']
            print(f"🔍 [Shopify] 通过名称查询发票: {draft_name}")
            
            # Get all draft orders and find the one with matching name
            draft_orders_data = client.get_draft_orders(limit=250)
            if 'error' in draft_orders_data:
                print(f"❌ [Shopify] 查询发票失败: {draft_orders_data['error']}")
                return {'error': draft_orders_data['error'], 'response': f"查询发票失败: {draft_orders_data['error']}"}
            
            draft_orders = draft_orders_data.get('draft_orders', [])
            # Find the draft order with matching name
            matching_order = None
            for order in draft_orders:
                if order.get('name') == draft_name:
                    matching_order = order
                    break
            
            if not matching_order:
                print(f"❌ [Shopify] 未找到发票: {draft_name}")
                return {
                    'error': f'未找到发票 {draft_name}',
                    'response': f"❌ 未找到发票 {draft_name}。\n\n请确认发票号是否正确，或使用以下命令查看所有发票：\n\"show me all invoices\""
                }
            
            # Found the matching draft order
            print(f"✅ [Shopify] 发票查询成功:")
            print(f"   发票号: {matching_order.get('name')}")
            print(f"   总金额: {matching_order.get('total_price')} {matching_order.get('currency')}")
            print(f"   状态: {matching_order.get('status')}")

            # 📋 Log API Response Data
            print(f"\n📦 [Shopify API Response] 发票详情:")
            print(f"      ID: {matching_order.get('id')}")
            print(f"      Name: {matching_order.get('name')}")
            print(f"      Email: {matching_order.get('email', 'N/A')}")
            print(f"      Total: {matching_order.get('total_price')} {matching_order.get('currency')}")
            print(f"      Status: {matching_order.get('status')}")
            print(f"      Invoice Sent At: {matching_order.get('invoice_sent_at', 'N/A')}")

            # 🔧 evaluation 明确指定这是单个发票的金额，避免LLM混淆
            response = self._format_single_invoice_amount(matching_order)
            
            # Return single draft order data
            draft_order_data = {'draft_order': matching_order}
            
            # 清理所有发票数据，只保留单个匹配的发票
            # 避免LLM从包含所有发票的draft_orders_data中读取错误信息
            draft_orders_data = draft_order_data
        
        elif 'draft_order_id' in params:
            # Get specific draft order by ID
            print(f"🔍 [Shopify] 查询发票详情: Draft Order ID = {params['draft_order_id']}")
            draft_order_data = client.get_draft_order(params['draft_order_id'])
            if 'error' in draft_order_data:
                print(f"❌ [Shopify] 查询发票失败: {draft_order_data['error']}")
                return {'error': draft_order_data['error'], 'response': f"查询发票失败: {draft_order_data['error']}"}
            
            draft_order = draft_order_data.get('draft_order', {})
            print(f"✅ [Shopify] 发票查询成功:")
            print(f"   发票号: #{draft_order.get('name', draft_order.get('id'))}")
            print(f"   总金额: {draft_order.get('total_price')} {draft_order.get('currency')}")
            print(f"   状态: {draft_order.get('status')}")
            
            # 📋 Log API Response Data
            print(f"\n📦 [Shopify API Response] 发票详情:")
            print(f"      ID: {draft_order.get('id')}")
            print(f"      Name: #{draft_order.get('name')}")
            print(f"      Email: {draft_order.get('email', 'N/A')}")
            print(f"      Total: {draft_order.get('total_price')} {draft_order.get('currency')}")
            print(f"      Status: {draft_order.get('status')}")
            print(f"      Invoice Sent At: {draft_order.get('invoice_sent_at', 'N/A')}")
            
            response = self._format_draft_order_details(draft_order)
        else:
            # Get multiple draft orders
            print(f"🔍 [Shopify] 查询发票列表:")
            print(f"   状态筛选: {params.get('status') or '全部'}")
            print(f"   返回数量: {params.get('limit', 10)}")
            draft_orders_data = client.get_draft_orders(
                status=params.get('status'),
                limit=params.get('limit', 10)
            )
            if 'error' in draft_orders_data:
                print(f"❌ [Shopify] 查询发票失败: {draft_orders_data['error']}")
                return {'error': draft_orders_data['error'], 'response': f"查询发票失败: {draft_orders_data['error']}"}
            
            draft_orders = draft_orders_data.get('draft_orders', [])
            print(f"✅ [Shopify] 发票列表查询成功:")
            print(f"   返回发票数: {len(draft_orders)}")
            if draft_orders:
                total_amount = sum(float(order.get('total_price', 0)) for order in draft_orders)
                currency = draft_orders[0].get('currency', 'USD')
                print(f"   总金额: {total_amount:.2f} {currency}")
                
            # 📋 Log API Response Data
            print(f"\n📦 [Shopify API Response] 发票数据:")
            for i, draft_order in enumerate(draft_orders[:5], 1):  # Show first 5 in log
                print(f"   Invoice {i}:")
                print(f"      ID: {draft_order.get('id')}")
                print(f"      Name: #{draft_order.get('name')}")
                print(f"      Total: {draft_order.get('total_price')} {draft_order.get('currency')}")
                print(f"      Status: {draft_order.get('status')}")
                print(f"      Customer: {draft_order.get('customer', {}).get('email', 'N/A')}")
                print(f"      Created: {draft_order.get('created_at', '')[:10]}")
            if len(draft_orders) > 5:
                print(f"   ... and {len(draft_orders) - 5} more invoices")
            
            response = self._format_draft_orders_list(draft_orders, params.get('status'))
        
        # Include raw API data for LLM context
        return {
            'response': response, 
            'data': draft_orders_data if 'draft_orders_data' in locals() else draft_order_data,
            'api_data': draft_orders_data if 'draft_orders_data' in locals() else draft_order_data  # For LLM context
        }
    
    def _format_draft_order_details(self, draft_order: Dict[str, Any]) -> str:
        """Format single draft order details"""
        customer = draft_order.get('customer', {})
        
        lines = [
            f"📄 发票详情",
            f"━━━━━━━━━━━━━━━━━━━━━━",
            f"发票号: #{draft_order.get('name', draft_order.get('id'))}",
            f"创建时间: {draft_order.get('created_at', '').split('T')[0]}",
            f"状态: {draft_order.get('status', 'unknown')}",
            f"总金额: {draft_order.get('total_price')} {draft_order.get('currency')}",
            f"税费: {draft_order.get('total_tax')} {draft_order.get('currency')}",
        ]
        
        if draft_order.get('invoice_sent_at'):
            lines.append(f"发票发送时间: {draft_order.get('invoice_sent_at', '').split('T')[0]}")
        else:
            lines.append(f"发票状态: 未发送")
        
        if draft_order.get('order_id'):
            lines.append(f"已转换为订单: #{draft_order.get('order_id')}")
        
        lines.extend([
            f"",
            f"👤 客户信息:",
            f"  姓名: {customer.get('first_name', '')} {customer.get('last_name', '')}",
            f"  邮箱: {customer.get('email', 'N/A')}",
            f"",
            f"📋 订单商品:"
        ])
        
        for item in draft_order.get('line_items', []):
            lines.append(f"  • {item.get('title')} x{item.get('quantity')} - {item.get('price')} {draft_order.get('currency')}")
        
        return "\n".join(lines)
    
    def _format_draft_orders_list(self, draft_orders: list, status: str = None) -> str:
        """Format list of draft orders"""
        if not draft_orders:
            return f"未找到{'符合条件的' if status else ''}发票。"
        
        lines = [
            f"📄 发票列表 (共{len(draft_orders)}个)",
            f"━━━━━━━━━━━━━━━━━━━━━━"
        ]
        
        for draft_order in draft_orders:
            customer = draft_order.get('customer', {})
            customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or customer.get('email', 'Guest')
            
            status_icon = {
                'open': '📝',
                'invoice_sent': '✉️',
                'completed': '✅'
            }.get(draft_order.get('status'), '❓')
            
            lines.append(
                f"{status_icon} #{draft_order.get('name')}: {draft_order.get('total_price')} {draft_order.get('currency')} | "
                f"{draft_order.get('status')} | {customer_name}"
            )
        
        return "\n".join(lines)

    def _format_single_invoice_amount(self, draft_order: Dict[str, Any]) -> str:
        """Format single invoice amount response (optimized for amount queries)"""
        customer = draft_order.get('customer', {})
        customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or customer.get('email', 'Guest')

        # 🔧 直接回答金额，避免LLM混淆为汇总数据
        return f"""📄 发票金额查询结果

发票: {draft_order.get('name')}
客户: {customer_name}
状态: {draft_order.get('status')}
金额: {draft_order.get('total_price')} {draft_order.get('currency')}

这是单个发票的准确金额信息。"""

    def handle_analysis_query(self, params: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle sales analysis query"""
        client = self.get_client(session_id)
        if not client:
            print(f"❌ [Shopify] 销售分析失败: 未认证")
            return {'error': '未认证', 'response': '请先配置Shopify凭证'}
        
        print(f"📊 [Shopify] 正在分析销售数据:")
        print(f"   分析周期: 过去 {params.get('days', 30)} 天")
        
        analysis = client.analyze_orders(days=params.get('days', 30))
        
        if 'error' in analysis:
            print(f"❌ [Shopify] 销售分析失败: {analysis['error']}")
            return {'error': analysis['error'], 'response': f"分析失败: {analysis['error']}"}
        
        print(f"✅ [Shopify] 销售分析完成:")
        print(f"   总订单数: {analysis.get('total_orders', 0)}")
        print(f"   总销售额: {analysis.get('total_revenue', 0)} {analysis.get('currency', 'USD')}")
        print(f"   平均订单价值: {analysis.get('average_order_value', 0)} {analysis.get('currency', 'USD')}")
        print(f"   热销产品数: {len(analysis.get('top_products', []))}")
        print(f"   优质客户数: {len(analysis.get('top_customers', []))}")
        
        # 📋 Log API Response Data
        print(f"\n📦 [Shopify API Response] 销售分析数据:")
        print(f"   Period: {analysis.get('period_days')} days")
        print(f"   Total Orders: {analysis.get('total_orders')}")
        print(f"   Total Revenue: {analysis.get('total_revenue')} {analysis.get('currency')}")
        print(f"   Avg Order Value: {analysis.get('average_order_value')}")
        if analysis.get('top_products'):
            print(f"   Top 3 Products:")
            for i, product in enumerate(analysis.get('top_products')[:3], 1):
                print(f"      {i}. {product.get('name')}: {product.get('quantity')} units")
        
        response = self._format_analysis(analysis)
        return {'response': response, 'data': analysis, 'api_data': analysis}
    
    def _format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format analysis results"""
        lines = [
            f"📊 销售数据分析 (过去{analysis['period_days']}天)",
            f"━━━━━━━━━━━━━━━━━━━━━━",
            f"",
            f"💰 财务概况:",
            f"  总订单数: {analysis['total_orders']}",
            f"  总销售额: {analysis['total_revenue']} {analysis['currency']}",
            f"  平均订单价值: {analysis['average_order_value']} {analysis['currency']}",
            f"",
            f"📈 订单状态:",
        ]
        
        for status, count in analysis.get('financial_status_breakdown', {}).items():
            lines.append(f"  {status}: {count}")
        
        lines.append(f"")
        lines.append(f"📦 发货状态:")
        for status, count in analysis.get('fulfillment_status_breakdown', {}).items():
            lines.append(f"  {status}: {count}")
        
        if analysis.get('top_products'):
            lines.append(f"")
            lines.append(f"🏆 热销产品 TOP 5:")
            for i, product in enumerate(analysis['top_products'][:5], 1):
                lines.append(f"  {i}. {product['name']}: {product['quantity']} 件")
        
        if analysis.get('top_customers'):
            lines.append(f"")
            lines.append(f"👑 优质客户 TOP 5:")
            for i, customer in enumerate(analysis['top_customers'][:5], 1):
                lines.append(f"  {i}. {customer['name']}: {customer['orders']}单 | {customer['total_spent']} {analysis['currency']}")
        
        return "\n".join(lines)
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user query with conversational interaction"""
        session_id = context.get('session_id', 'default') if context else 'default'
        
        print(f"\n{'='*60}")
        print(f"🛍️ [Shopify Agent] 处理查询请求")
        print(f"{'='*60}")
        print(f"查询内容: {query}")
        print(f"Session ID: {session_id}")
        
        # 🔧 自动检测并使用环境变量中的凭证
        if not self.is_authenticated(session_id):
            import os
            env_shop_url = os.environ.get('SHOPIFY_SHOP_URL', '').strip() or os.environ.get('SHOPIFY_SHOP_DOMAIN', '').strip()
            env_access_token = os.environ.get('SHOPIFY_ACCESS_TOKEN', '').strip()
            
            if env_shop_url and env_access_token:
                print(f"🔑 [Shopify] 检测到环境变量配置，自动连接...")
                print(f"   Shop URL: {env_shop_url}")
                # 自动使用环境变量进行认证
                auth_result = self.set_credentials(session_id, env_shop_url, env_access_token)
                if not auth_result.get('success'):
                    print(f"⚠️ [Shopify] 环境变量认证失败: {auth_result.get('message')}")
        
        print(f"认证状态: {'✅ 已连接' if self.is_authenticated(session_id) else '❌ 未连接'}")
        
        if self.is_authenticated(session_id):
            shop_info = self.session_credentials[session_id].get('shop_info', {})
            print(f"当前商店: {shop_info.get('name', 'Unknown')} ({shop_info.get('domain', 'N/A')})")
        
        # 强制禁用网络搜索和RAG（Shopify助手只能使用Shopify API）
        if context:
            context['web_search_enabled'] = False
            context['rag_enabled'] = False
            context['deep_research_enabled'] = False
            if 'web_search_results' in context:
                del context['web_search_results']
            if 'rag_results' in context:
                del context['rag_results']
        
        # Detect intent
        intent_data = self.detect_intent(query)
        intent = intent_data['intent']
        params = intent_data['params']
        
        print(f"识别意图: {intent}")
        if params:
            print(f"提取参数: {params}")
        
        # Handle different intents
        if intent == 'auth':
            result = self.handle_auth_request(query, params, session_id)
        
        elif intent == 'logout':
            print(f"🔓 [Shopify] 断开连接: Session ID = {session_id}")
            self.clear_credentials(session_id)
            print(f"✅ [Shopify] 凭证已清除")
            result = {
                'response': "✅ 已断开Shopify连接并清除凭证。",
                'authenticated': False
            }
        
        elif not self.is_authenticated(session_id):
            # Not authenticated, prompt for credentials
            result = {
                'response': "您还未连接到Shopify商店。\n\n" + 
                           self.handle_auth_request('', {}, session_id)['response'],
                'authenticated': False,
                'awaiting_credentials': True
            }
        
        elif intent == 'orders':
            result = self.handle_orders_query(params, session_id)
        
        elif intent == 'fulfillments':
            if 'order_id' not in params:
                print(f"⚠️ [Shopify] 查询发货信息失败: 缺少订单ID")
                result = {'response': '请提供订单ID来查询发货信息。例如：\"查询订单1234567890的发货信息\"'}
            else:
                print(f"🚚 [Shopify] 查询发货信息: Order ID = {params['order_id']}")
                client = self.get_client(session_id)
                fulfillments = client.get_fulfillments(params['order_id'])
                if 'error' in fulfillments:
                    print(f"❌ [Shopify] 查询发货信息失败: {fulfillments['error']}")
                else:
                    fulfillment_count = len(fulfillments.get('fulfillments', []))
                    print(f"✅ [Shopify] 发货信息查询成功: {fulfillment_count} 条发货记录")
                result = {'response': self._format_fulfillments(fulfillments), 'data': fulfillments}
        
        elif intent == 'transactions':
            if 'order_id' not in params:
                print(f"⚠️ [Shopify] 查询交易信息失败: 缺少订单ID")
                result = {'response': '请提供订单ID来查询交易信息。例如：\"查询订单1234567890的交易记录\"'}
            else:
                print(f"💳 [Shopify] 查询交易记录: Order ID = {params['order_id']}")
                client = self.get_client(session_id)
                transactions = client.get_transactions(params['order_id'])
                if 'error' in transactions:
                    print(f"❌ [Shopify] 查询交易记录失败: {transactions['error']}")
                else:
                    transaction_count = len(transactions.get('transactions', []))
                    print(f"✅ [Shopify] 交易记录查询成功: {transaction_count} 条交易记录")
                result = {'response': self._format_transactions(transactions), 'data': transactions}
        
        elif intent == 'customers':
            client = self.get_client(session_id)
            if 'search_query' in params:
                print(f"👥 [Shopify] 搜索客户: 关键词 = \"{params['search_query']}\", 限制 = {params.get('limit', 10)}")
                customers = client.search_customers(params['search_query'], params.get('limit', 10))
            else:
                print(f"👥 [Shopify] 查询客户列表: 限制 = {params.get('limit', 10)}")
                customers = client.get_customers(params.get('limit', 10))
            
            if 'error' in customers:
                print(f"❌ [Shopify] 客户查询失败: {customers['error']}")
            else:
                customer_count = len(customers.get('customers', []))
                print(f"✅ [Shopify] 客户查询成功: {customer_count} 个客户")
            result = {'response': self._format_customers(customers), 'data': customers}
        
        elif intent == 'products':
            print(f"🛍️ [Shopify] 查询产品列表: 限制 = {params.get('limit', 10)}")
            client = self.get_client(session_id)
            products = client.get_products(params.get('limit', 10))
            if 'error' in products:
                print(f"❌ [Shopify] 产品查询失败: {products['error']}")
            else:
                product_count = len(products.get('products', []))
                print(f"✅ [Shopify] 产品查询成功: {product_count} 个产品")
            result = {'response': self._format_products(products), 'data': products}
        
        elif intent == 'invoices':
            result = self.handle_invoice_query(params, session_id)
        
        elif intent == 'analysis':
            result = self.handle_analysis_query(params, session_id)
        
        elif intent == 'shop_info':
            print(f"🏪 [Shopify] 查询商店信息")
            client = self.get_client(session_id)
            shop_info = client.get_shop_info()
            if 'error' in shop_info:
                print(f"❌ [Shopify] 商店信息查询失败: {shop_info['error']}")
            else:
                print(f"✅ [Shopify] 商店信息查询成功:")
                print(f"   商店名称: {shop_info.get('shop', {}).get('name', 'N/A')}")
                print(f"   商店域名: {shop_info.get('shop', {}).get('domain', 'N/A')}")
            result = {'response': self._format_shop_info(shop_info), 'data': shop_info}
        
        else:
            # General query - use LLM to generate response with context
            print(f"💬 [Shopify] 处理一般性查询（使用LLM生成响应）")
            shop_info = self.session_credentials.get(session_id, {}).get('shop_info', {})
            prompt = f"""作为Shopify助手，请回答用户的问题。

用户已连接的商店信息:
{shop_info if shop_info else '(未连接)'}

用户问题: {query}

请提供有帮助的回答，如果用户想要查询特定数据，引导他们使用更具体的查询，例如：
- \"显示最近10个订单\"
- \"分析最近30天的销售数据\"
- \"查询订单1234567890的详情\"
- \"查看发货状态\"
"""
            response = self.generate_response(prompt)
            print(f"✅ [Shopify] LLM响应已生成")
            result = {'response': response}
        
        # 输出查询结果日志
        print(f"\n{'─'*60}")
        print(f"✅ [Shopify] 查询处理完成")
        if 'error' in result:
            print(f"❌ 错误信息: {result['error']}")
        else:
            response_preview = result.get('response', '')[:200]
            if len(result.get('response', '')) > 200:
                response_preview += '...'
            print(f"📝 响应预览: {response_preview}")
            if result.get('data'):
                print(f"📦 已返回数据对象")
                # Log that data is being passed to LLM context
                print(f"🔗 API数据将被用作LLM上下文输入")
        print(f"{'='*60}\n")
        
        # Build context for LLM from API data
        api_context = ""
        if result.get('data'):
            import json
            api_context = f"\n\n=== Shopify API Data ===\n{json.dumps(result.get('data'), indent=2, ensure_ascii=False)}\n"
            print(f"📊 [LLM Context] API数据已添加到上下文 ({len(api_context)} 字符)")
        
        return {
            'agent': self.name,
            'query': query,
            'response': result.get('response', '') + api_context if context and context.get('include_raw_data') else result.get('response', ''),
            'timestamp': datetime.now().isoformat(),
            'specialization': self.get_specialization(),
            'authenticated': self.is_authenticated(session_id),
            'intent': intent,
            'data': result.get('data'),  # Raw API data
            'api_data': result.get('data'),  # Explicit API data for LLM context
            'shopify_data': result.get('data')  # Shopify-specific data marker
        }
    
    def _format_fulfillments(self, data: Dict[str, Any]) -> str:
        """Format fulfillments data"""
        if 'error' in data:
            return f"查询失败: {data['error']}"
        
        fulfillments = data.get('fulfillments', [])
        if not fulfillments:
            return "该订单还没有发货记录。"
        
        lines = ["📦 发货信息", "━━━━━━━━━━━━━━━━━━━━━━"]
        for ful in fulfillments:
            lines.append(f"发货ID: {ful.get('id')}")
            lines.append(f"状态: {ful.get('status')}")
            lines.append(f"跟踪号: {ful.get('tracking_number', 'N/A')}")
            lines.append(f"物流公司: {ful.get('tracking_company', 'N/A')}")
            lines.append(f"创建时间: {ful.get('created_at', '').split('T')[0]}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_transactions(self, data: Dict[str, Any]) -> str:
        """Format transactions data"""
        if 'error' in data:
            return f"查询失败: {data['error']}"
        
        transactions = data.get('transactions', [])
        if not transactions:
            return "该订单没有交易记录。"
        
        lines = ["💳 交易记录", "━━━━━━━━━━━━━━━━━━━━━━"]
        for trans in transactions:
            lines.append(f"交易ID: {trans.get('id')}")
            lines.append(f"金额: {trans.get('amount')} {trans.get('currency')}")
            lines.append(f"类型: {trans.get('kind')}")
            lines.append(f"状态: {trans.get('status')}")
            lines.append(f"网关: {trans.get('gateway', 'N/A')}")
            lines.append(f"时间: {trans.get('created_at', '').split('T')[0]}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_customers(self, data: Dict[str, Any]) -> str:
        """Format customers data"""
        if 'error' in data:
            return f"查询失败: {data['error']}"
        
        customers = data.get('customers', [])
        if not customers:
            return "未找到客户记录。"
        
        lines = [f"👤 客户列表 (共{len(customers)}位)", "━━━━━━━━━━━━━━━━━━━━━━"]
        for customer in customers:
            name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or 'Guest'
            lines.append(f"{name} | {customer.get('email')} | 订单数: {customer.get('orders_count', 0)}")
        
        return "\n".join(lines)
    
    def _format_products(self, data: Dict[str, Any]) -> str:
        """Format products data"""
        if 'error' in data:
            return f"查询失败: {data['error']}"
        
        products = data.get('products', [])
        if not products:
            return "未找到产品。"
        
        lines = [f"🛍️ 产品列表 (共{len(products)}个)", "━━━━━━━━━━━━━━━━━━━━━━"]
        for product in products:
            variants = product.get('variants', [])
            price = variants[0].get('price') if variants else 'N/A'
            lines.append(f"{product.get('title')} | {price} | 状态: {product.get('status')}")
        
        return "\n".join(lines)
    
    def _format_shop_info(self, data: Dict[str, Any]) -> str:
        """Format shop info"""
        if 'error' in data:
            return f"查询失败: {data['error']}"
        
        shop = data.get('shop', {})
        lines = [
            "🏪 商店信息",
            "━━━━━━━━━━━━━━━━━━━━━━",
            f"商店名称: {shop.get('name')}",
            f"商店域名: {shop.get('domain')}",
            f"电子邮件: {shop.get('email')}",
            f"货币: {shop.get('currency')}",
            f"时区: {shop.get('timezone')}",
            f"国家: {shop.get('country_name')}",
            f"创建时间: {shop.get('created_at', '').split('T')[0]}"
        ]

        return "\n".join(lines)

    def _format_single_order_amount(self, order: Dict[str, Any]) -> str:
        """Format single order amount response (optimized for amount queries)"""
        customer = order.get('customer', {})
        customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or customer.get('email', 'Guest')

        # 🔧 直接回答金额，避免LLM混淆为汇总数据
        return f"""📦 订单金额查询结果

订单: #{order.get('name')}
客户: {customer_name}
状态: {order.get('financial_status')}
金额: {order.get('total_price')} {order.get('currency')}

这是单个订单的准确金额信息。"""


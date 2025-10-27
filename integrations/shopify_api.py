"""
Shopify API Integration Module
Provides functionality to connect with Shopify API and query store data
Supports both environment variables and user-provided credentials
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class ShopifyAPIClient:
    """Client for interacting with Shopify Admin API"""
    
    def __init__(self, shop_url: str = None, access_token: str = None):
        """
        Initialize Shopify API client
        
        Args:
            shop_url: The shop domain (e.g., 'your-shop.myshopify.com')
            access_token: Admin API access token
        """
        # Support both SHOPIFY_SHOP_URL and SHOPIFY_SHOP_DOMAIN for backward compatibility
        self.shop_url = (shop_url or 
                        os.environ.get('SHOPIFY_SHOP_URL', '').strip() or 
                        os.environ.get('SHOPIFY_SHOP_DOMAIN', '').strip())
        self.access_token = access_token or os.environ.get('SHOPIFY_ACCESS_TOKEN', '').strip()
        
        print(f"🔧 [Shopify API] 初始化客户端")
        print(f"   Shop URL: {self.shop_url if self.shop_url else '❌ 未配置'}")
        print(f"   Access Token: {'✅ 已配置' if self.access_token else '❌ 未配置'}")
        
        # Ensure shop_url has proper format
        if self.shop_url:
            # Remove any protocol if present
            self.shop_url = self.shop_url.replace('https://', '').replace('http://', '')
            # Ensure .myshopify.com domain
            if not self.shop_url.endswith('.myshopify.com'):
                if '.' not in self.shop_url:
                    self.shop_url = f"{self.shop_url}.myshopify.com"
            self.base_url = f"https://{self.shop_url}/admin/api/2024-01"
        else:
            self.base_url = None
        
        # Headers for API requests
        self.headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        } if self.access_token else {}
    
    def is_configured(self) -> bool:
        """Check if API credentials are configured"""
        return bool(self.shop_url and self.access_token and self.base_url)
    
    def update_credentials(self, shop_url: str, access_token: str) -> None:
        """
        Update API credentials
        
        Args:
            shop_url: The shop domain
            access_token: Admin API access token
        """
        self.__init__(shop_url, access_token)
    
    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make API request to Shopify
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., '/orders.json')
            params: Query parameters
            data: Request body data
            
        Returns:
            API response data
        """
        if not self.is_configured():
            return {
                'error': 'Shopify API未配置',
                'message': '请先设置商店URL和访问令牌'
            }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method, 
                url, 
                headers=self.headers, 
                params=params,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.content else {'success': True}
        except requests.exceptions.HTTPError as e:
            error_msg = f'Shopify API请求失败: {str(e)}'
            try:
                error_detail = e.response.json() if e.response.content else {}
                error_msg = f"{error_msg} - {error_detail.get('errors', error_detail)}"
            except:
                pass
            return {
                'error': error_msg,
                'status_code': e.response.status_code if hasattr(e, 'response') else None
            }
        except requests.exceptions.RequestException as e:
            return {
                'error': f'网络请求失败: {str(e)}',
                'message': '请检查网络连接和商店URL是否正确'
            }
    
    # Order Management
    def get_orders(self, status: str = None, limit: int = 50, since_id: int = None, fields: str = None) -> Dict[str, Any]:
        """
        Get orders from Shopify store
        
        Args:
            status: Filter by status (any, open, closed, cancelled)
            limit: Maximum number of orders to return (max 250)
            since_id: Get orders with ID greater than this value
            fields: Comma-separated list of fields to return
            
        Returns:
            List of orders
        """
        params = {'limit': min(limit, 250)}
        
        if status:
            params['status'] = status
        if since_id:
            params['since_id'] = since_id
        if fields:
            params['fields'] = fields
        
        return self._make_request('GET', '/orders.json', params)
    
    def get_order(self, order_id: int) -> Dict[str, Any]:
        """Get specific order by ID"""
        return self._make_request('GET', f'/orders/{order_id}.json')
    
    def get_order_count(self, status: str = None) -> Dict[str, Any]:
        """Get count of orders"""
        params = {'status': status} if status else {}
        return self._make_request('GET', '/orders/count.json', params)
    
    def count_orders(self, status: str = None) -> Dict[str, Any]:
        """Alias for get_order_count for backward compatibility"""
        return self.get_order_count(status)
    
    # Fulfillment Management
    def get_fulfillments(self, order_id: int = None) -> Dict[str, Any]:
        """Get fulfillments (shipping information)"""
        if order_id:
            return self._make_request('GET', f'/orders/{order_id}/fulfillments.json')
        return {'error': '需要提供订单ID'}
    
    def get_fulfillment(self, order_id: int, fulfillment_id: int) -> Dict[str, Any]:
        """Get specific fulfillment by ID"""
        return self._make_request('GET', f'/orders/{order_id}/fulfillments/{fulfillment_id}.json')
    
    # Transaction Management (Billing)
    def get_transactions(self, order_id: int) -> Dict[str, Any]:
        """Get transactions (billing information) for an order"""
        return self._make_request('GET', f'/orders/{order_id}/transactions.json')
    
    def get_transaction(self, order_id: int, transaction_id: int) -> Dict[str, Any]:
        """Get specific transaction by ID"""
        return self._make_request('GET', f'/orders/{order_id}/transactions/{transaction_id}.json')
    
    # Customer Information
    def get_customers(self, limit: int = 50, since_id: int = None, fields: str = None) -> Dict[str, Any]:
        """Get customers from store"""
        params = {'limit': min(limit, 250)}
        if since_id:
            params['since_id'] = since_id
        if fields:
            params['fields'] = fields
        return self._make_request('GET', '/customers.json', params)
    
    def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Get specific customer by ID"""
        return self._make_request('GET', f'/customers/{customer_id}.json')
    
    def search_customers(self, query: str, limit: int = 50) -> Dict[str, Any]:
        """Search customers by query (email, phone, name, etc.)"""
        params = {'query': query, 'limit': min(limit, 250)}
        return self._make_request('GET', '/customers/search.json', params)
    
    # Product Information
    def get_products(self, limit: int = 50, since_id: int = None, fields: str = None) -> Dict[str, Any]:
        """Get products from store"""
        params = {'limit': min(limit, 250)}
        if since_id:
            params['since_id'] = since_id
        if fields:
            params['fields'] = fields
        return self._make_request('GET', '/products.json', params)
    
    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get specific product by ID"""
        return self._make_request('GET', f'/products/{product_id}.json')
    
    def get_product_count(self) -> Dict[str, Any]:
        """Get count of products"""
        return self._make_request('GET', '/products/count.json')
    
    def count_products(self) -> Dict[str, Any]:
        """Alias for get_product_count for backward compatibility"""
        return self.get_product_count()
    
    # Store/Shop Information
    def get_shop_info(self) -> Dict[str, Any]:
        """Get shop information"""
        return self._make_request('GET', '/shop.json')
    
    # Draft Orders (Invoices)
    def get_draft_orders(self, limit: int = 50, since_id: int = None, status: str = None, fields: str = None) -> Dict[str, Any]:
        """
        Get draft orders (used for invoices)
        
        Args:
            limit: Maximum number of draft orders to retrieve (default: 50, max: 250)
            since_id: Retrieve draft orders after this ID
            status: Filter by status ('open', 'invoice_sent', 'completed')
            fields: Comma-separated list of fields to retrieve
            
        Returns:
            Draft orders data
        """
        params = {'limit': min(limit, 250)}
        if since_id:
            params['since_id'] = since_id
        if status:
            params['status'] = status
        if fields:
            params['fields'] = fields
        
        return self._make_request('GET', '/draft_orders.json', params=params)
    
    def get_draft_order(self, draft_order_id: int) -> Dict[str, Any]:
        """Get a specific draft order by ID"""
        return self._make_request('GET', f'/draft_orders/{draft_order_id}.json')
    
    def get_draft_order_count(self, status: str = None) -> Dict[str, Any]:
        """
        Get count of draft orders
        
        Args:
            status: Filter by status ('open', 'invoice_sent', 'completed')
        """
        params = {}
        if status:
            params['status'] = status
        return self._make_request('GET', '/draft_orders/count.json', params=params)
    
    def send_invoice(self, draft_order_id: int, custom_message: str = None) -> Dict[str, Any]:
        """
        Send invoice email to customer for a draft order
        
        Args:
            draft_order_id: The draft order ID
            custom_message: Optional custom message to include in the invoice email
            
        Returns:
            Draft order invoice data
        """
        data = {}
        if custom_message:
            data['draft_order_invoice'] = {
                'to': None,  # Will use customer's email from draft order
                'subject': None,  # Will use default subject
                'custom_message': custom_message
            }
        
        return self._make_request('POST', f'/draft_orders/{draft_order_id}/send_invoice.json', data=data)
    
    def complete_draft_order(self, draft_order_id: int, payment_pending: bool = False) -> Dict[str, Any]:
        """
        Complete a draft order and convert it to an order
        
        Args:
            draft_order_id: The draft order ID
            payment_pending: Whether payment is pending (default: False)
            
        Returns:
            Completed draft order data with order information
        """
        data = {'payment_pending': payment_pending}
        return self._make_request('PUT', f'/draft_orders/{draft_order_id}/complete.json', data=data)
    
    # Analytical Reports
    def analyze_orders(self, days: int = 30, status: str = 'any') -> Dict[str, Any]:
        """
        Analyze orders for the specified number of days
        
        Args:
            days: Number of days to analyze
            status: Order status filter
            
        Returns:
            Analysis summary with statistics
        """
        orders_data = self.get_orders(status=status, limit=250)
        
        if 'error' in orders_data:
            return orders_data
        
        orders = orders_data.get('orders', [])
        
        if not orders:
            return {
                'message': '未找到订单',
                'period_days': days,
                'total_orders': 0
            }
        
        # Calculate totals
        total_revenue = sum(float(order.get('total_price', 0)) for order in orders)
        total_orders = len(orders)
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Count by financial status
        status_counts = {}
        for order in orders:
            fin_status = order.get('financial_status', 'unknown')
            status_counts[fin_status] = status_counts.get(fin_status, 0) + 1
        
        # Count by fulfillment status
        fulfillment_counts = {}
        for order in orders:
            ful_status = order.get('fulfillment_status') or 'unfulfilled'
            fulfillment_counts[ful_status] = fulfillment_counts.get(ful_status, 0) + 1
        
        # Get top products
        product_counts = {}
        for order in orders:
            for line_item in order.get('line_items', []):
                product_title = line_item.get('title', 'Unknown')
                quantity = int(line_item.get('quantity', 0))
                product_counts[product_title] = product_counts.get(product_title, 0) + quantity
        
        top_products = []
        if product_counts:
            top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Get top customers
        customer_orders = {}
        for order in orders:
            customer = order.get('customer', {})
            if customer:
                customer_id = customer.get('id')
                customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                if customer_id:
                    if customer_id not in customer_orders:
                        customer_orders[customer_id] = {
                            'name': customer_name or customer.get('email', 'Unknown'),
                            'email': customer.get('email', ''),
                            'orders': 0,
                            'total_spent': 0
                        }
                    customer_orders[customer_id]['orders'] += 1
                    customer_orders[customer_id]['total_spent'] += float(order.get('total_price', 0))
        
        top_customers = sorted(
            customer_orders.values(), 
            key=lambda x: x['total_spent'], 
            reverse=True
        )[:5]
        
        return {
            'period_days': days,
            'total_orders': total_orders,
            'total_revenue': round(total_revenue, 2),
            'average_order_value': round(average_order_value, 2),
            'financial_status_breakdown': status_counts,
            'fulfillment_status_breakdown': fulfillment_counts,
            'top_products': [{'name': name, 'quantity': qty} for name, qty in top_products],
            'top_customers': top_customers,
            'currency': orders[0].get('currency', 'USD') if orders else 'USD',
            'analyzed_orders': total_orders
        }


class ShopifySessionManager:
    """Manages Shopify credentials per conversation session"""
    
    def __init__(self):
        self.session_credentials: Dict[str, Dict[str, str]] = {}
    
    def set_credentials(self, session_id: str, shop_url: str, access_token: str) -> bool:
        """
        Store Shopify credentials for a session
        
        Args:
            session_id: Conversation session ID
            shop_url: Shopify shop URL
            access_token: API access token
            
        Returns:
            True if successful
        """
        self.session_credentials[session_id] = {
            'shop_url': shop_url,
            'access_token': access_token,
            'timestamp': datetime.now().isoformat()
        }
        return True
    
    def get_credentials(self, session_id: str) -> Optional[Dict[str, str]]:
        """Get credentials for a session"""
        return self.session_credentials.get(session_id)
    
    def has_credentials(self, session_id: str) -> bool:
        """Check if session has credentials"""
        return session_id in self.session_credentials
    
    def clear_credentials(self, session_id: str) -> bool:
        """Clear credentials for a session"""
        if session_id in self.session_credentials:
            del self.session_credentials[session_id]
            return True
        return False
    
    def get_client(self, session_id: str) -> Optional[ShopifyAPIClient]:
        """Get configured Shopify client for session"""
        creds = self.get_credentials(session_id)
        if creds:
            return ShopifyAPIClient(
                shop_url=creds['shop_url'],
                access_token=creds['access_token']
            )
        return None


# Global instances
_shopify_client = None
_session_manager = ShopifySessionManager()

def get_shopify_client(shop_url: str = None, access_token: str = None) -> ShopifyAPIClient:
    """
    Get or create Shopify API client instance
    
    Args:
        shop_url: Optional shop URL (uses env if not provided)
        access_token: Optional access token (uses env if not provided)
    """
    if shop_url or access_token:
        return ShopifyAPIClient(shop_url, access_token)
    
    global _shopify_client
    if _shopify_client is None:
        _shopify_client = ShopifyAPIClient()
    return _shopify_client

def get_session_manager() -> ShopifySessionManager:
    """Get the global session manager"""
    return _session_manager

def test_connection(shop_url: str = None, access_token: str = None) -> Dict[str, Any]:
    """Test Shopify API connection"""
    client = get_shopify_client(shop_url, access_token)
    
    if not client.is_configured():
        return {
            'success': False,
            'message': 'Shopify API未配置',
            'configured': False
        }
    
    # Try to get shop info
    shop_info = client.get_shop_info()
    
    if 'error' in shop_info:
        return {
            'success': False,
            'message': shop_info.get('error', '连接失败'),
            'configured': True,
            'error_details': shop_info
        }
    
    shop_data = shop_info.get('shop', {})
    return {
        'success': True,
        'message': '连接成功',
        'configured': True,
        'shop_name': shop_data.get('name', 'Unknown'),
        'shop_domain': shop_data.get('domain', 'Unknown'),
        'shop_email': shop_data.get('email', ''),
        'currency': shop_data.get('currency', 'USD'),
        'timezone': shop_data.get('timezone', '')
    }


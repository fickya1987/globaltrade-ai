import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/contexts/AuthContext'
import { 
  TrendingUp, 
  Users, 
  MessageSquare, 
  Globe,
  ArrowUpRight,
  Activity,
  DollarSign,
  Package
} from 'lucide-react'

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    totalProducts: 12,
    activeConversations: 8,
    marketResearch: 5,
    monthlyGrowth: 15.2
  })

  const recentActivities = [
    {
      id: 1,
      type: 'message',
      title: 'New message from Italian Coffee Roasters',
      description: 'Interested in your Sumatra coffee beans',
      time: '2 hours ago',
      badge: 'New'
    },
    {
      id: 2,
      type: 'research',
      title: 'Market research completed',
      description: 'Coffee market analysis for Italy is ready',
      time: '4 hours ago',
      badge: 'Completed'
    },
    {
      id: 3,
      type: 'contact',
      title: 'New contact discovered',
      description: '5 potential buyers found in Germany',
      time: '1 day ago',
      badge: 'Discovery'
    }
  ]

  const quickActions = [
    {
      title: 'Start Market Research',
      description: 'Find buyers for your products',
      icon: <Globe className="w-5 h-5" />,
      href: '/market-research',
      color: 'bg-blue-500'
    },
    {
      title: 'Add New Product',
      description: 'List a new product for export',
      icon: <Package className="w-5 h-5" />,
      href: '/products',
      color: 'bg-green-500'
    },
    {
      title: 'Chat with Buyers',
      description: 'Continue conversations',
      icon: <MessageSquare className="w-5 h-5" />,
      href: '/chat',
      color: 'bg-purple-500'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-green-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">
          Welcome back, {user?.full_name || 'User'}! 👋
        </h1>
        <p className="text-blue-100 mb-4">
          Here's what's happening with your export business today
        </p>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center">
            <Activity className="w-4 h-4 mr-1" />
            <span>All systems operational</span>
          </div>
          <div className="flex items-center">
            <Globe className="w-4 h-4 mr-1" />
            <span>Connected to global markets</span>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Products</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalProducts}</div>
            <p className="text-xs text-muted-foreground">
              +2 from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Chats</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeConversations}</div>
            <p className="text-xs text-muted-foreground">
              +3 new conversations
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Market Research</CardTitle>
            <Globe className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.marketResearch}</div>
            <p className="text-xs text-muted-foreground">
              2 completed this week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Growth</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">+{stats.monthlyGrowth}%</div>
            <p className="text-xs text-muted-foreground">
              vs last month
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Get started with common tasks
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {quickActions.map((action, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="w-full justify-start h-auto p-4"
                  asChild
                >
                  <a href={action.href}>
                    <div className={`w-8 h-8 rounded-md ${action.color} flex items-center justify-center text-white mr-3`}>
                      {action.icon}
                    </div>
                    <div className="text-left">
                      <div className="font-medium">{action.title}</div>
                      <div className="text-xs text-muted-foreground">{action.description}</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 ml-auto" />
                  </a>
                </Button>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Your latest business updates and notifications
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivities.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                      {activity.type === 'message' && <MessageSquare className="w-4 h-4 text-blue-600" />}
                      {activity.type === 'research' && <Globe className="w-4 h-4 text-green-600" />}
                      {activity.type === 'contact' && <Users className="w-4 h-4 text-purple-600" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {activity.title}
                        </p>
                        <Badge variant="secondary" className="ml-2">
                          {activity.badge}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        {activity.description}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {activity.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* AI Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="w-5 h-5 mr-2 text-blue-600" />
            AI Insights & Recommendations
          </CardTitle>
          <CardDescription>
            Personalized suggestions to grow your export business
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h3 className="font-medium text-blue-900 mb-2">Market Opportunity</h3>
              <p className="text-sm text-blue-700 mb-3">
                Italian coffee market shows 23% growth. Your Sumatra coffee could be a perfect fit.
              </p>
              <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                Explore Italy Market
              </Button>
            </div>
            
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <h3 className="font-medium text-green-900 mb-2">Product Optimization</h3>
              <p className="text-sm text-green-700 mb-3">
                Adding organic certification could increase your product appeal by 40%.
              </p>
              <Button size="sm" variant="outline" className="border-green-600 text-green-600 hover:bg-green-600 hover:text-white">
                Learn More
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


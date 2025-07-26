import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Search, Globe, TrendingUp } from 'lucide-react'

export default function MarketResearch() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Market Research</h1>
          <p className="text-gray-600">Discover global opportunities for your products</p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Search className="w-4 h-4 mr-2" />
          Start New Research
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Globe className="w-5 h-5 mr-2 text-blue-600" />
              Global Markets
            </CardTitle>
            <CardDescription>
              Explore international markets for your products
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              AI-powered analysis of global market opportunities, demand patterns, and competitive landscape.
            </p>
            <Button variant="outline" className="w-full">
              Explore Markets
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
              Market Trends
            </CardTitle>
            <CardDescription>
              Stay updated with latest market trends
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Real-time insights into market trends, pricing patterns, and emerging opportunities.
            </p>
            <Button variant="outline" className="w-full">
              View Trends
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Search className="w-5 h-5 mr-2 text-purple-600" />
              Contact Discovery
            </CardTitle>
            <CardDescription>
              Find verified business contacts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Discover potential buyers, distributors, and partners with verified contact information.
            </p>
            <Button variant="outline" className="w-full">
              Find Contacts
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Coming Soon</CardTitle>
          <CardDescription>
            Advanced market research features are being developed
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            This page will include comprehensive market research tools, AI-powered insights, 
            and contact discovery features to help you expand your export business globally.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}


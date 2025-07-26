import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Package, Plus, Upload, Share } from 'lucide-react'

export default function ProductsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-600">Manage your export products and listings</p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Plus className="w-4 h-4 mr-2" />
          Add Product
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Package className="w-5 h-5 mr-2 text-blue-600" />
              Product Catalog
            </CardTitle>
            <CardDescription>
              Manage your product listings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Create and manage detailed product listings with photos, specifications, and pricing.
            </p>
            <Button variant="outline" className="w-full">
              View Catalog
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Upload className="w-5 h-5 mr-2 text-green-600" />
              Media Upload
            </CardTitle>
            <CardDescription>
              Upload product images and videos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Upload high-quality images, videos, and documents to showcase your products.
            </p>
            <Button variant="outline" className="w-full">
              Upload Media
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Share className="w-5 h-5 mr-2 text-purple-600" />
              Social Sharing
            </CardTitle>
            <CardDescription>
              Share products on social media
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Share your products on social media platforms to reach more potential buyers.
            </p>
            <Button variant="outline" className="w-full">
              Share Products
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Coming Soon</CardTitle>
          <CardDescription>
            Advanced product management features are being developed
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            This page will include comprehensive product management tools, media upload capabilities, 
            social media integration, and AI-powered product optimization suggestions.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}


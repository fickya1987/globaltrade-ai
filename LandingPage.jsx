import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Globe, 
  MessageSquare, 
  TrendingUp, 
  Users, 
  Zap, 
  Shield,
  ArrowRight,
  CheckCircle,
  Star,
  Play
} from 'lucide-react'

export default function LandingPage() {
  const [isVideoPlaying, setIsVideoPlaying] = useState(false)

  const features = [
    {
      icon: <Globe className="w-6 h-6" />,
      title: "Global Market Research",
      description: "AI-powered market analysis to find the perfect buyers for your products worldwide"
    },
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: "Real-time Translation",
      description: "Communicate with international clients in their language with voice and text translation"
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Business Intelligence",
      description: "Get insights and recommendations to grow your export business"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Contact Discovery",
      description: "Find verified business contacts and potential partners in target markets"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "AI Multi-Agent System",
      description: "Multiple AI agents working together to optimize your export operations"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Secure Platform",
      description: "Enterprise-grade security for your business data and communications"
    }
  ]

  const testimonials = [
    {
      name: "Ahmad Wijaya",
      company: "Indonesian Coffee Exports",
      location: "Jakarta, Indonesia",
      text: "GlobalTrade AI helped me connect with Italian coffee roasters. The translation feature made negotiations seamless!",
      rating: 5
    },
    {
      name: "Maria Santos",
      company: "Brazilian Textiles Co.",
      location: "São Paulo, Brazil", 
      text: "The market research insights were incredible. We expanded to 3 new countries in just 6 months.",
      rating: 5
    },
    {
      name: "David Chen",
      company: "Tech Components Ltd",
      location: "Shenzhen, China",
      text: "Real-time voice translation during video calls changed everything. No more language barriers!",
      rating: 5
    }
  ]

  const useCaseSteps = [
    {
      step: "1",
      title: "Upload Your Product",
      description: "Add your Sumatra coffee details, photos, and specifications to the platform"
    },
    {
      step: "2", 
      title: "AI Market Analysis",
      description: "Our AI analyzes Italian coffee market trends, competitors, and opportunities"
    },
    {
      step: "3",
      title: "Find Italian Buyers",
      description: "Get verified contacts of Italian coffee roasters and distributors"
    },
    {
      step: "4",
      title: "Communicate Seamlessly",
      description: "Chat and call Italian buyers with real-time translation support"
    },
    {
      step: "5",
      title: "Close the Deal",
      description: "Negotiate and finalize export contracts with AI-powered business insights"
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Globe className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">GlobalTrade AI</span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">Features</a>
              <a href="#how-it-works" className="text-gray-600 hover:text-blue-600 transition-colors">How it Works</a>
              <a href="#testimonials" className="text-gray-600 hover:text-blue-600 transition-colors">Testimonials</a>
              <Link to="/login">
                <Button variant="ghost">Login</Button>
              </Link>
              <Link to="/register">
                <Button>Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <Badge className="mb-4 bg-blue-100 text-blue-800 hover:bg-blue-200">
              🚀 AI-Powered Export Platform
            </Badge>
            
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Export Your Products
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-green-600">
                {" "}Globally
              </span>
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Connect with international buyers, communicate in any language, and grow your export business 
              with our AI multi-agent platform. From market research to closing deals - we've got you covered.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Link to="/register">
                <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3">
                  Start Exporting Today
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
              
              <Button 
                variant="outline" 
                size="lg" 
                className="px-8 py-3"
                onClick={() => setIsVideoPlaying(true)}
              >
                <Play className="mr-2 w-5 h-5" />
                Watch Demo
              </Button>
            </div>

            {/* Use Case Example */}
            <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 max-w-2xl mx-auto border border-gray-200">
              <div className="flex items-center justify-center mb-4">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <span className="font-medium">🇮🇩 Indonesia</span>
                  <ArrowRight className="w-4 h-4" />
                  <span className="font-medium">🇮🇹 Italy</span>
                </div>
              </div>
              <p className="text-gray-700 font-medium">
                "I want to sell my premium Sumatra coffee to Italian roasters"
              </p>
              <p className="text-sm text-gray-500 mt-2">
                See how GlobalTrade AI makes this possible ↓
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for Global Trade
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to succeed in international markets, powered by advanced AI technology
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
                <CardHeader>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                    <div className="text-blue-600">
                      {feature.icon}
                    </div>
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              From Coffee Bean to Italian Espresso
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              See how a coffee farmer in Indonesia can sell to Italy using GlobalTrade AI
            </p>
          </div>

          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-1/2 transform -translate-x-px h-full w-0.5 bg-blue-200 hidden lg:block"></div>
            
            <div className="space-y-12">
              {useCaseSteps.map((step, index) => (
                <div key={index} className={`relative flex items-center ${index % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'}`}>
                  {/* Step number */}
                  <div className="absolute left-1/2 transform -translate-x-1/2 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg z-10 hidden lg:flex">
                    {step.step}
                  </div>
                  
                  {/* Content */}
                  <div className={`w-full lg:w-5/12 ${index % 2 === 0 ? 'lg:pr-12' : 'lg:pl-12'}`}>
                    <Card className="border-0 shadow-lg">
                      <CardHeader>
                        <div className="flex items-center space-x-3 lg:hidden">
                          <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                            {step.step}
                          </div>
                          <CardTitle className="text-xl">{step.title}</CardTitle>
                        </div>
                        <CardTitle className="text-xl hidden lg:block">{step.title}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <CardDescription className="text-gray-600">
                          {step.description}
                        </CardDescription>
                      </CardContent>
                    </Card>
                  </div>
                  
                  {/* Spacer for opposite side */}
                  <div className="hidden lg:block w-5/12"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Success Stories from Around the World
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              See how businesses are growing their exports with GlobalTrade AI
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="border-0 shadow-lg">
                <CardContent className="pt-6">
                  <div className="flex mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-700 mb-6 italic">"{testimonial.text}"</p>
                  <div>
                    <p className="font-semibold text-gray-900">{testimonial.name}</p>
                    <p className="text-sm text-gray-600">{testimonial.company}</p>
                    <p className="text-sm text-gray-500">{testimonial.location}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-green-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Go Global?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of exporters who are growing their business with AI-powered global trade
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3">
                Start Your Free Trial
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" size="lg" className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-3">
                Sign In
              </Button>
            </Link>
          </div>

          <div className="mt-8 flex items-center justify-center space-x-6 text-blue-100">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 mr-2" />
              <span>Free 14-day trial</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 mr-2" />
              <span>No credit card required</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Globe className="w-6 h-6 text-blue-400" />
                <span className="text-lg font-bold">GlobalTrade AI</span>
              </div>
              <p className="text-gray-400">
                Empowering businesses to export globally with AI-powered tools and real-time communication.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#how-it-works" className="hover:text-white transition-colors">How it Works</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 GlobalTrade AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}


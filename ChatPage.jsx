import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { MessageSquare, Mic, Video, Languages } from 'lucide-react'

export default function ChatPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Chat & Communication</h1>
          <p className="text-gray-600">Connect with international buyers and partners</p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <MessageSquare className="w-4 h-4 mr-2" />
          New Conversation
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <MessageSquare className="w-5 h-5 mr-2 text-blue-600" />
              Text Chat
            </CardTitle>
            <CardDescription>
              Real-time messaging with translation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Chat with buyers worldwide with automatic translation support for seamless communication.
            </p>
            <Button variant="outline" className="w-full">
              Start Chat
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Mic className="w-5 h-5 mr-2 text-green-600" />
              Voice Calls
            </CardTitle>
            <CardDescription>
              Real-time voice communication
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Make voice calls with real-time translation powered by OpenAI Voice API.
            </p>
            <Button variant="outline" className="w-full">
              Start Call
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Video className="w-5 h-5 mr-2 text-purple-600" />
              Video Calls
            </CardTitle>
            <CardDescription>
              Face-to-face meetings with translation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Video conferences with live translation and cultural context assistance.
            </p>
            <Button variant="outline" className="w-full">
              Start Video
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Coming Soon</CardTitle>
          <CardDescription>
            Advanced communication features are being developed
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            This page will include real-time chat, voice and video calling with AI translation, 
            media sharing, and cultural context assistance for international business communication.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}


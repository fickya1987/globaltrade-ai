import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

const LoadingSpinner = ({ size = "md", className, ...props }) => {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6", 
    lg: "w-8 h-8",
    xl: "w-12 h-12"
  }

  return (
    <Loader2 
      className={cn("animate-spin", sizeClasses[size], className)} 
      {...props} 
    />
  )
}

export default LoadingSpinner


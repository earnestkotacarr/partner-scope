function ChatMessage({ role, content }) {
  const isUser = role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-md'
            : 'bg-slate-100 text-slate-800 rounded-bl-md'
        }`}
      >
        {/* Render content with basic markdown support */}
        <div className="whitespace-pre-wrap">
          {content.split('\n').map((line, i) => {
            // Handle bold text
            const parts = line.split(/(\*\*.*?\*\*)/)
            return (
              <p key={i} className={i > 0 ? 'mt-2' : ''}>
                {parts.map((part, j) => {
                  if (part.startsWith('**') && part.endsWith('**')) {
                    return (
                      <strong key={j} className="font-semibold">
                        {part.slice(2, -2)}
                      </strong>
                    )
                  }
                  return part
                })}
              </p>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage

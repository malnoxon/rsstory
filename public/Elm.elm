import Graphics.Input.Field as Field
import Graphics.Input as Input
import Http
import String
import Text
import Window
import Debug


main : Signal Element
main = scene <~ Window.dimensions
              ~ lift3 form first.signal last.signal errors

-- Signals and Inputs
first  = Input.input Field.noContent
last   = Input.input Field.noContent
email  = Input.input Field.noContent
remail = Input.input Field.noContent
submit = Input.input ()

XhasAttempted : Signal Bool
hasAttempted =
    let isPositive c = c > 0
    in  isPositive <~ count submit.signal

sendable : Signal Bool
sendable = keepWhen hasAttempted False (isEmpty <~ errors)

errors : Signal [String]
errors =
    let rawErrors = lift2 getErrors first.signal last.signal
    in  keepWhen hasAttempted [] <| merge rawErrors (sampleOn submit.signal rawErrors)

getErrors : Field.Content -> Field.Content -> [String]
getErrors first last =
    let empty content = String.isEmpty content.string
        checks = [ (empty first , "URL Required")
                 , (empty last  , "Time required")
                 ]
        activeError (err,msg) = if err then Just msg else Nothing
    in
        justs <| map activeError checks

port redirect : Signal String
port redirect =
    let f = first.signal
    in
      keepWhen sendable "" <| sampleOn submit.signal <| lift (\x -> x.string) f


--url : Field.Constent -> String

responses : Signal (Http.Response String)
responses =
      Http.send (lift2 (\x y -> Http.post  "http://127.0.0.1:8000/pyrss2gen.xml" (x.string ++ " " ++ y.string))  first.signal last.signal)



--url : Field.Content -> Field.Content -> Field.Content -> String
--url first last email = 
   --Debug.log "d" ("/login?first=" ++ first.string ++ "&last=" ++ last.string ++ "&email="++ email.string)

getLogin : Signal String -> Signal (Http.Response String)
getLogin req = responses


-- Display
scene : (Int,Int) -> Element -> Element
scene (w,h) form =
    color charcoal . flow down <|
      [ spacer w 50
      , container w (h-50) midTop form
      ]

form : Field.Content -> Field.Content -> [String] -> Element
form first' last' errors =
    color lightGrey . flow down <|
      [ container 340 60 middle . leftAligned . Text.height 32 <| toText "RSStory"
      , field "URL:"     first.handle  first'
      , field "Time (sec):"      last.handle   last'
      , showErrors errors
      , container 300 50 midRight <| size 60 30 <| Input.button submit.handle () "Submit"
      ]

field : String -> Input.Handle Field.Content -> Field.Content -> Element
field label handle content =
  flow right
    [ container 120 36 midRight <| plainText label
    , container 220 36 middle <| size 180 26 <|
      Field.field Field.defaultStyle handle id "" content
    ]

showErrors : [String] -> Element
showErrors errs =
  flow down
    [ spacer 10 10
    , if isEmpty errs
        then spacer 0 0
        else flow down <| map (width 340 . centered . Text.color red . toText) errs
    ]

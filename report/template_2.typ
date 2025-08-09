#set heading(numbering: "1.")
#show heading.where(level: 1): it => block[
  #box(fill: white, width: 100%)[
    #grid(columns: (3fr, 1fr), align: (left + bottom))[
      #it.body
    ][
      #box(width: 80pt, height: 80pt, fill: blue)[
        #align(center + horizon)[
          #text(size: 22pt, fill: white)[
            #counter(heading).display()
          ]
        ]
      ]
    ]
  ]
]

#let info(title, body) = [
  #box(fill: blue.lighten(90%), inset: (x: 12pt, y: 10pt), radius: 8pt)[
    #smallcaps()[#text(fill: blue)[*#title*]]
    #v(-2mm)
    #par(justify: true)[
      #text(size: 9pt)[
        #body
      ]
    ]
  ]
]

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


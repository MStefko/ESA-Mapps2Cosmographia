Frame kernel for JUICE solar panels. The Stardust spacecraft
NAIF id is used because I can't be bothered to figure out how to
register a custom spacecraft in SPICE right now.

Note that frame center is centered around JUICE (id 28)

   \begindata
   
      FRAME_STARDUST_SPACECRAFT        = -29000
      FRAME_-29000_NAME             = 'STARDUST_SPACECRAFT'
      FRAME_-29000_CLASS            = 3
      FRAME_-29000_CLASS_ID         = -29000
      FRAME_-29000_CENTER           = -28
      CK_-29000_SCLK                = -29
      CK_-29000_SPK                 = -29
   
   \begintext
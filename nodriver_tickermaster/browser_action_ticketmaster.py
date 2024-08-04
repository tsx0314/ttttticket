import nodriver as uc

async def login(page):
    try:
        login = await page.select("a[href*=login]")
    except TimeoutError as e:
        print(e)

# <a class="btn btn-primary btn-block btn-findTickets nav-ticket" href="/activity/game/24sg_zerobaseone" rel="nofollow">BUY TICKETS</a>
# <a class="btn btn-primary text-bold m-0" href="https://ticketmaster.sg/ticket/area/24sg_txt/1719" rel="nofollow" data-href="https://ticketmaster.sg/ticket/area/24sg_txt/1719">Find tickets</a>
# <g id="field_PEND_VIP" class="empty">
	# 	<g>
	# 		<polygon fill="#b9e7df" points="439.4,283.6 438.1,275.1 562.2,342.2 563.4,350.7 			"></polygon>
	# 	</g>
	# 	<g>
	# 		<polygon fill="#b9e7df" points="561.9,342.4 563,350.2 439.7,283.4 438.5,275.6 			"></polygon>
	# 	</g>
	# 	<g>
	# 		<polygon fill="#bcede5" points="561.6,342.3 595.5,318.5 596.7,327 562.8,350.7 			"></polygon>
	# 	</g>
	# 	<g>
	# 		<polygon fill="#bcede5" points="595.3,319 596.4,326.9 563,350.2 561.9,342.4 			"></polygon>
	# 	</g>
	# 	<g>
	# 		<polygon fill="#bdeee6" points="438,275.6 471.9,251.9 595.8,319 561.9,342.7 			"></polygon>
	# 	</g>
	# 	<g>
	# 		<polygon fill="#bdeee6" points="471.9,252.2 595.3,319 561.9,342.4 438.5,275.6 			"></polygon>
	# 	</g>
	# </g>
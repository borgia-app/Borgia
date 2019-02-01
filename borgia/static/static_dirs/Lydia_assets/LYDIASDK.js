
(function ($) {
	function LYDIAProcess() {

		this.configKey	= [
			'vendor_token',
			'amount',
			'recipient',
			'order_ref',
			'browser_success_url',
			'browser_cancel_url',
			'confirm_url',
			'sale_desc',
			'payer_desc',
			'collector_desc',
			'expire_time',
			'end_date',
			'provider_token',
			'payment_recipient',
			'notify_payer',
			'notify_collector',
			'display_conf',
			'payment_method',
			'env',
			'render'
		];

		this.configToSkip = [
			'env',
			'render'
		]

		this.data = {
			vendor_token		: "",
			amount				: "",
			recipient			: "",
			order_ref 			: "",
			browser_success_url : "",
			browser_cancel_url 	: "",
			confirm_url 		: "",
			sale_desc 			: "",
			payer_desc 			: "",
			collector_desc 		: "",
			expire_time 		: "",
			end_date 			: "",
			provider_token 		: "",
			payment_recipient	: "",
			notify_payer 		: "",
			notify_collector 	: "",
			display_conf 		: "",
			payment_method		: "auto",
			currency			: "EUR",
			type				: "phone"
		}


		this.baseUrl	= "https://lydia-app.com/";
		this.isRunning 	= false;
	}

	LYDIAProcess.prototype.sendRequest = function() {
		if (this.isRunning == false) {
			this.isRunning = true;
			$.post(this.baseUrl+"api/request/do.json",
				   this.data,
   				   function(data) {
				 	if (data.error == 0) {
				 		document.location = data.mobile_url;
				 	} else {
					 	console.log(data);
				 	}
				}
			);
		}
	};

	$.fn.payWithLYDIA = function(data) {

		var lydiaProcess = new LYDIAProcess();

		for (var i = 0; i < lydiaProcess.configKey.length; i++) {
			if (lydiaProcess.configToSkip.indexOf(lydiaProcess.configKey[i]) < 0 && data[lydiaProcess.configKey[i]] != undefined) {
				lydiaProcess.data[lydiaProcess.configKey[i]] = data[lydiaProcess.configKey[i]];
			}
		}

		if (data.env && data.env == 'test') {
			lydiaProcess.baseUrl	= "https://homologation.lydia-app.com/";
		}

		if (data.render) {
			$(this).html(data.render);
		} else {
			$(this).html('<a href="#" onclick="return false;"><img class="lydia_payment_button" src="'+lydiaProcess.baseUrl+'assets/img/paymentbutton.png" height="40" /></a>');
		}

		$(this).click(function () {
			lydiaProcess.sendRequest();
		});
	}

}(jQuery))

<?php
/**
 * Dashboard preset query panel.
 *
 * @package WPVDB_Playground_Demo
 */

defined( 'ABSPATH' ) || exit;
?>

<div id="wpvdb-demo-presets" class="postbox">
	<div class="postbox-header">
		<h2 class="hndle"><?php esc_html_e( 'Playground demo queries', 'wpvdb-playground-demo' ); ?></h2>
	</div>
	<div class="inside">
		<p><?php esc_html_e( 'Run preset vector searches against the sample content.', 'wpvdb-playground-demo' ); ?></p>
		<div class="wpvdb-demo-presets__buttons"></div>
		<div class="wpvdb-demo-presets__results" role="status" aria-live="polite"></div>
	</div>
</div>

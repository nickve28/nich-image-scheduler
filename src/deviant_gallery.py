import argparse
import time
from datetime import datetime
from clients.deviant import DeviantClient
from utils.account_loader import select_account
from colorama import init, Fore

init(autoreset=True)

parser = argparse.ArgumentParser(
    description="Fetch deviations from a DeviantArt user's gallery",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("account_id", help="Account ID to use for authentication")
parser.add_argument("username", help="DeviantArt username to fetch deviations from")
parser.add_argument("--offset", type=int, default=0, help="Starting position for pagination (default: 0)")
parser.add_argument("--limit", type=int, default=24, help="Number of deviations to retrieve (max 24, default: 24)")
parser.add_argument("--fix-resolution", action="store_true", help="Fix display resolution to 1920px for images wider than 1920px")
parser.add_argument("--delay", type=float, default=1.0, help="Delay in seconds between edit requests (default: 1.0)")
parser.add_argument("--num-iterations", type=int, default=1, help="Number of iterations to fetch and process (default: 1)")
parser.add_argument("--iterations-delay", type=float, default=0.0, help="Delay in seconds between iterations (default: 0.0)")

args = parser.parse_args()

account = select_account(args.account_id)
deviant_account_name = args.username
offset = args.offset
limit = args.limit

print(f"Fetching deviations for account {deviant_account_name}")
print(f"Offset: {offset}, Limit: {limit}, Iterations: {args.num_iterations}")
print("\n")

client = DeviantClient(account)

# Track if we should exit early due to failure
should_exit = False

for iteration in range(args.num_iterations):
    if should_exit:
        break

    if iteration > 0:
        print(f"\n{'='*80}")
        print(f"Iteration {iteration + 1}/{args.num_iterations}")
        print(f"{'='*80}\n")

    response, access_token = client.get_all_deviations(deviant_account_name, offset=offset, limit=limit)

    if "results" in response:
        print(f"Found {len(response['results'])} deviations:")

        for idx, deviation in enumerate(response["results"], start=offset + 1):
            title = deviation['title']
            deviationid = deviation['deviationid']
            url = deviation['url']
            mature = deviation.get('is_mature', False)
            published_date = "N/A"
            published_time = deviation.get('published_time')
            if published_time:
                published_date = datetime.fromtimestamp(int(published_time)).strftime('%Y-%m-%d %H:%M:%S')
            width = "N/A"
            height = "N/A"
            if 'content' in deviation:
                content = deviation['content']
                width = content.get('width', 'N/A')
                height = content.get('height', 'N/A')
            favs = 0
            comments = 0
            if 'stats' in deviation:
                stats = deviation['stats']
                favs = stats.get('favourites', 0)
                comments = stats.get('comments', 0)

            # Highlight width in red if greater than 1920
            dimensions = f"{width}x{height}"
            needs_fix = width != "N/A" and int(width) > 1920

            if needs_fix:
                dimensions = Fore.RED + dimensions + Fore.RESET

            print(f"#{idx}: {deviationid}, {dimensions}, {published_date}, '{title}', {url}, {favs} favs, {comments} comments, Mature: {mature}")

            if needs_fix:
                # Fix resolution if flag is enabled
                if args.fix_resolution:
                    print(f"  Fixing resolution for {deviationid}...")
                    result = client.edit_deviation_resolution(deviationid, display_resolution=8, access_token=access_token)
                    if result.get('status') == 'success':
                        print(Fore.GREEN + f"  ✓ Successfully set resolution to 1920px" + Fore.RESET)
                    else:
                        print(Fore.RED + f"  ✗ Failed to update: {result}" + Fore.RESET)
                        print(Fore.RED + "Exiting early due to failure." + Fore.RESET)
                        should_exit = True
                        break

                    # Add delay between requests to avoid rate limiting
                    time.sleep(args.delay)

        if should_exit:
            break

        # Update offset for next iteration
        if response.get('has_more'):
            next_offset = response.get('next_offset', offset + limit)
            print(f"\nMore deviations available. Next offset: {next_offset}")
            offset = next_offset

            # Add delay between iterations if configured and not the last iteration
            if args.iterations_delay > 0 and iteration < args.num_iterations - 1:
                print(f"Waiting {args.iterations_delay} seconds before next iteration...")
                time.sleep(args.iterations_delay)
        else:
            print("\nNo more deviations.")
            break
    else:
        print(f"Error fetching deviations: {response}")
        break
